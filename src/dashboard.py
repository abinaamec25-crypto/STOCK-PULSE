from pathlib import Path
from typing import List, Dict, Any
from collections import defaultdict
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

def generate_dashboard_report(items: List[Dict[str, Any]], reorders: List[Dict[str, Any]], anomalies: List[Dict[str, Any]], out_file: Path):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Executive_Dashboard"
    ws.views.sheetView[0].showGridLines = True

    total_skus = len(items)
    total_val = sum(it["Stock_Valuation_INR"] for it in items)
    reorder_count = len(reorders)
    neg_stock_count = sum(1 for it in items if it["Current_Balance"] < 0)
    critical_count = sum(1 for it in items if "CRITICAL" in it["Status"] or "OUT OF STOCK" in it["Status"])
    unknown_codes = sum(1 for a in anomalies if a.get("error_type") == "UNKNOWN_CODE")
    total_po_cost = sum(r["Estimated_PO_Cost_INR"] for r in reorders)

    # Banner
    ws.merge_cells("A1:G1")
    tcell = ws["A1"]
    tcell.value = "DEFINEINFOTECH (DIT) — OPERATIONS INVENTORY MONITORING DASHBOARD"
    tcell.font = Font(name="Calibri", size=14, bold=True, color="FFFFFF")
    tcell.fill = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
    tcell.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 32

    # KPI Cards
    kpis = [
        ("MONITORED SKUs", str(total_skus), "1E3A8A", "DBEAFE"),
        ("TOTAL VALUATION", f"₹ {total_val:,.2f}", "047857", "D1FAE5"),
        ("REORDER ALERTS", str(reorder_count), "B45309", "FEF3C7"),
        ("NEGATIVE STOCK", str(neg_stock_count), "B91C1C", "FEE2E2"),
        ("UNKNOWN CODES", str(unknown_codes), "6D28D9", "EDE9FE"),
        ("EST. PO BUDGET", f"₹ {total_po_cost:,.2f}", "4338CA", "E0E7FF")
    ]
    card_cols = ["A", "B", "C", "D", "E", "F"]
    for i, (title, val, text_c, fill_c) in enumerate(kpis):
        col = card_cols[i]
        ws[f"{col}3"] = title
        ws[f"{col}3"].font = Font(name="Calibri", size=9, bold=True, color="475569")
        ws[f"{col}3"].alignment = Alignment(horizontal="center")
        ws[f"{col}3"].fill = PatternFill(start_color=fill_c, fill_type="solid")
        ws[f"{col}4"] = val
        ws[f"{col}4"].font = Font(name="Calibri", size=13, bold=True, color=text_c)
        ws[f"{col}4"].alignment = Alignment(horizontal="center")
        ws[f"{col}4"].fill = PatternFill(start_color=fill_c, fill_type="solid")
    ws.row_dimensions[3].height = 20
    ws.row_dimensions[4].height = 28

    # Category Table
    ws["A6"] = "CATEGORY PERFORMANCE"
    ws["A6"].font = Font(name="Calibri", size=11, bold=True, color="1E3A8A")
    cat_headers = ["Category", "SKU Count", "Total Current Balance", "Total Valuation (INR)", "Reorders Needed"]
    ws.append([]) # row 7
    ws.append(cat_headers) # row 8
    for c in ws[8]:
        c.fill = PatternFill(start_color="334155", fill_type="solid")
        c.font = Font(name="Calibri", size=10, bold=True, color="FFFFFF")

    cat_stats = defaultdict(lambda: {"count": 0, "balance": 0.0, "val": 0.0, "reorders": 0})
    for it in items:
        cat = it["Category"]
        cat_stats[cat]["count"] += 1
        cat_stats[cat]["balance"] += it["Current_Balance"]
        cat_stats[cat]["val"] += it["Stock_Valuation_INR"]
        if it["Reorder_Required"] == "YES":
            cat_stats[cat]["reorders"] += 1

    for cat, s in sorted(cat_stats.items()):
        ws.append([cat, s["count"], s["balance"], s["val"], s["reorders"]])

    for col in ws.columns:
        col_letter = get_column_letter(col[0].column)
        max_l = max(len(str(c.value or "")) for c in col if c.row > 1)
        ws.column_dimensions[col_letter].width = max(max_l + 4, 14)

    wb.save(out_file)
