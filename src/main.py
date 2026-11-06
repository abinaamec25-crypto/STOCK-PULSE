import sys
from pathlib import Path
from typing import List, Dict, Any, Tuple
from collections import defaultdict
import openpyxl

current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from logger import setup_logger, log_audit_error
from validation import (
    normalize_column_name,
    validate_and_sanitize_master_record,
    validate_and_sanitize_transaction
)
from business_rules import calculate_stock_balance, evaluate_reorder, classify_stock_health
from report_generator import export_stock_report, export_reorder_list, export_exception_report
from dashboard import generate_dashboard_report


def scan_sheet_headers(ws: openpyxl.worksheet.worksheet.Worksheet, is_tx: bool = False) -> Tuple[int, Dict[int, str]]:
    """Scan the first 15 rows of a worksheet to identify the actual header row."""
    rows = list(ws.iter_rows(values_only=True))
    for row_idx, r in enumerate(rows[:15]):
        if not r or not any(r):
            continue
        col_map = {}
        for c_idx, val in enumerate(r):
            if val is not None and str(val).strip():
                canonical = normalize_column_name(val, is_tx=is_tx)
                col_map[c_idx] = canonical
        matched = set(col_map.values())
        if any(k in matched for k in ["Product_ID", "Product_Name", "Transaction_ID"]) or \
           ("Current_Stock" in matched and ("Unit_Price" in matched or "Supplier" in matched)):
            return row_idx, col_map

    # Fallback to row 0
    col_map = {c_idx: normalize_column_name(val) for c_idx, val in enumerate(rows[0]) if val is not None} if rows else {}
    return 0, col_map


def run_pipeline(input_excel: Path, output_dir: Path, log_file: Path) -> Dict[str, Any]:
    logger = setup_logger(log_file)
    logger.info("=================================================================")
    logger.info("Universal StockPulse AI Pipeline Ingestion Initiated")
    logger.info(f"Target: {input_excel}")
    output_dir.mkdir(parents=True, exist_ok=True)

    wb = openpyxl.load_workbook(input_excel, data_only=True)

    # 1. Sheet Classification (Master vs Transactions)
    master_ws = None
    tx_ws = None

    for s in wb.worksheets:
        t_low = s.title.lower()
        if "master" in t_low or "product" in t_low or "catalog" in t_low or "stock" in t_low:
            if not master_ws:
                master_ws = s
        elif "trans" in t_low or "tx" in t_low or "move" in t_low or "log" in t_low:
            if not tx_ws:
                tx_ws = s

    # If only one sheet exists, or master not identified, active is master
    if not master_ws:
        master_ws = wb.active
    if tx_ws == master_ws:
        tx_ws = None

    # If 2 sheets exist and tx_ws wasn't named explicitly, check second sheet
    if not tx_ws and len(wb.worksheets) > 1:
        other_sheets = [s for s in wb.worksheets if s != master_ws]
        if other_sheets:
            tx_ws = other_sheets[0]

    logger.info(f"Master Sheet Selected: '{master_ws.title}'")
    if tx_ws:
        logger.info(f"Transactions Sheet Selected: '{tx_ws.title}'")
    else:
        logger.info("Operating in Single-Sheet Master Inventory Mode")

    # 2. Ingest Master Sheet
    m_row_idx, m_col_map = scan_sheet_headers(master_ws, is_tx=False)
    m_rows = list(master_ws.iter_rows(values_only=True))[m_row_idx + 1:]

    valid_master: Dict[str, Dict[str, Any]] = {}
    anomalies: List[Dict[str, Any]] = []
    seen_ids = set()

    for idx, r in enumerate(m_rows, start=m_row_idx + 2):
        if not any(r):
            continue
        raw_dict = {}
        for c_idx, canonical in m_col_map.items():
            if c_idx < len(r):
                raw_dict[canonical] = r[c_idx]

        ok, reason, sanitized = validate_and_sanitize_master_record(raw_dict, seen_ids, idx)
        if ok:
            pid = sanitized["Product_ID"]
            seen_ids.add(pid)
            valid_master[pid] = sanitized
        else:
            anomalies.append({
                "error_type": "MASTER_DATA_ANOMALY",
                "id": raw_dict.get("Product_ID", f"Row-{idx}"),
                "raw": raw_dict,
                "reason": reason
            })
            log_audit_error(log_file, "MASTER_ANOMALY", raw_dict.get("Product_ID", f"Row-{idx}"), reason)

    # 3. Ingest Transactions Sheet (if present)
    stock_in_map = defaultdict(float)
    stock_out_map = defaultdict(float)
    valid_tx: List[Dict[str, Any]] = []

    if tx_ws:
        t_row_idx, t_col_map = scan_sheet_headers(tx_ws, is_tx=True)
        t_rows = list(tx_ws.iter_rows(values_only=True))[t_row_idx + 1:]
        for idx, r in enumerate(t_rows, start=t_row_idx + 2):
            if not any(r):
                continue
            raw_tx = {}
            for c_idx, canonical in t_col_map.items():
                if c_idx < len(r):
                    raw_tx[canonical] = r[c_idx]

            ok, reason, clean_tx = validate_and_sanitize_transaction(raw_tx, seen_ids, idx)
            if ok:
                pid = clean_tx["Product_ID"]
                qty = clean_tx["Quantity"]
                if clean_tx["Transaction_Type"] == "STOCK_IN":
                    stock_in_map[pid] += qty
                else:
                    stock_out_map[pid] += qty
                valid_tx.append(clean_tx)
            else:
                err_type = "UNKNOWN_CODE" if "Unknown Product Code" in reason else "INVALID_TRANSACTION"
                tx_ident = str(raw_tx.get("Transaction_ID") or raw_tx.get("Product_ID") or f"TxRow-{idx}")
                anomalies.append({
                    "error_type": err_type,
                    "id": tx_ident,
                    "raw": raw_tx,
                    "reason": reason
                })
                log_audit_error(log_file, err_type, tx_ident, reason)

    # 4. Calculate Balances, Deficits, and Reorders
    calculated_items: List[Dict[str, Any]] = []
    reorder_list: List[Dict[str, Any]] = []

    for pid, m in valid_master.items():
        opening = m["Opening_Stock"]
        total_in = stock_in_map[pid]
        total_out = stock_out_map[pid]
        
        # If transactions exist, calculate dynamic balance; else use current stock
        if tx_ws:
            current_balance = calculate_stock_balance(opening, total_in, total_out)
        else:
            current_balance = m.get("Current_Stock", opening)

        min_stock = m["Minimum_Stock"]
        reorder_qty = m["Reorder_Quantity"]
        price = m["Unit_Price"]

        status = classify_stock_health(current_balance, min_stock)
        reorder_req = evaluate_reorder(current_balance, min_stock)
        deficit = max(0.0, round(min_stock - current_balance, 2))
        rec_order = reorder_qty if reorder_req == "YES" else 0.0
        val = max(0.0, round(current_balance * price, 2))
        po_cost = round(rec_order * price, 2)

        item_dict = {
            **m,
            "Stock_IN": total_in,
            "Stock_OUT": total_out,
            "Current_Balance": current_balance,
            "Status": status,
            "Reorder_Required": reorder_req,
            "Stock_Deficit": deficit,
            "Recommended_Order_Qty": rec_order,
            "Stock_Valuation_INR": val,
            "Estimated_PO_Cost_INR": po_cost
        }
        calculated_items.append(item_dict)

        if current_balance < 0:
            anomalies.append({
                "error_type": "NEGATIVE_STOCK_ALERT",
                "id": pid,
                "raw": {"Opening": opening, "In": total_in, "Out": total_out, "Balance": current_balance},
                "reason": f"Negative Stock Balance ({current_balance} units). Stock over-issued without sufficient receipts."
            })
            log_audit_error(log_file, "NEGATIVE_STOCK", pid, f"Overdrawn balance: {current_balance}")

        if reorder_req == "YES":
            reorder_list.append(item_dict)

    # 5. Export Standard Excel Deliverables
    export_stock_report(calculated_items, output_dir / "Stock_Report.xlsx")
    export_reorder_list(reorder_list, output_dir / "Reorder_List.xlsx")
    export_exception_report(anomalies, output_dir / "Error_Report.xlsx")
    generate_dashboard_report(calculated_items, reorder_list, anomalies, output_dir / "Dashboard_Report.xlsx")
    wb.save(output_dir / "Master_and_Transactions_Archived.xlsx")

    unknown_count = sum(1 for a in anomalies if a.get("error_type") == "UNKNOWN_CODE")
    neg_count = sum(1 for it in calculated_items if it["Current_Balance"] < 0)

    logger.info(f"Ingestion Finished: {len(calculated_items)} Master SKUs | {len(valid_tx)} Transactions | {len(reorder_list)} Reorders")

    return {
        "valid_count": len(calculated_items),
        "transactions_processed": len(valid_tx),
        "reorder_count": len(reorder_list),
        "unknown_code_count": unknown_count,
        "negative_stock_count": neg_count,
        "total_valuation": sum(it["Stock_Valuation_INR"] for it in calculated_items),
        "total_po_cost": sum(r["Estimated_PO_Cost_INR"] for r in reorder_list),
        "anomalies_logged": len(anomalies),
        "records": calculated_items,
        "transactions": valid_tx,
        "anomalies": anomalies
    }

def main():
    inp = project_root / "input" / "Input_Data.xlsx"
    out = project_root / "output"
    log = project_root / "logs" / "error_log.txt"
    res = run_pipeline(inp, out, log)
    print("PIPELINE RESULT:", res)

if __name__ == "__main__":
    main()
