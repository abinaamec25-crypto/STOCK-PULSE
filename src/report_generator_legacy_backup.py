from pathlib import Path
from typing import List, Dict, Any
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

NAVY_FILL = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
STEEL_FILL = PatternFill(start_color="334155", end_color="334155", fill_type="solid")
HEADER_FONT = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
TITLE_FONT = Font(name="Calibri", size=13, bold=True, color="1E3A8A")
REGULAR_FONT = Font(name="Calibri", size=10)
THIN_BORDER = Border(
    left=Side(style="thin", color="CBD5E1"),
    right=Side(style="thin", color="CBD5E1"),
    top=Side(style="thin", color="CBD5E1"),
    bottom=Side(style="thin", color="CBD5E1")
)

def style_table(ws, title_text: str):
    ws.insert_rows(1, 2)
    ws.merge_cells("A1:J1")
    tcell = ws["A1"]
    tcell.value = title_text
    tcell.font = TITLE_FONT
    tcell.alignment = Alignment(vertical="center")
    ws.row_dimensions[1].height = 28
    ws.row_dimensions[3].height = 24
    for cell in ws[3]:
        cell.fill = NAVY_FILL
        cell.font = HEADER_FONT
        cell.alignment = Alignment(horizontal="center", vertical="center")
    for row in ws.iter_rows(min_row=4, max_row=ws.max_row):
        for cell in row:
            cell.font = REGULAR_FONT
            cell.border = THIN_BORDER
    for col in ws.columns:
        col_letter = get_column_letter(col[0].column)
        max_l = max(len(str(c.value or "")) for c in col if c.row > 2)
        ws.column_dimensions[col_letter].width = max(max_l + 4, 13)

def export_stock_report(items: List[Dict[str, Any]], out_file: Path):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Warehouse_Stock_Report"
    headers = [
        "Product_ID", "Product_Name", "Category", "Opening_Stock",
        "Stock_IN", "Stock_OUT", "Current_Balance", "Minimum_Stock",
        "Status", "Valuation_INR", "Warehouse_Location"
    ]
    ws.append(headers)
    for it in items:
        ws.append([
            it["Product_ID"], it["Product_Name"], it["Category"], it["Opening_Stock"],
            it["Stock_IN"], it["Stock_OUT"], it["Current_Balance"], it["Minimum_Stock"],
            it["Status"], it["Stock_Valuation_INR"], it["Warehouse_Location"]
        ])
    style_table(ws, "DEFINEINFOTECH (DIT) — WAREHOUSE STOCK BALANCE & VALUATION REPORT")
    wb.save(out_file)

def export_reorder_list(reorders: List[Dict[str, Any]], out_file: Path):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Reorder_Recommendations"
    headers = [
        "Product_ID", "Product_Name", "Current_Balance", "Minimum_Stock",
        "Deficit_Units", "Recommended_Reorder_Qty", "Unit_Price_INR",
        "Estimated_PO_Cost_INR", "Supplier", "Supplier_Contact", "Location"
    ]
    ws.append(headers)
    for r in reorders:
        ws.append([
            r["Product_ID"], r["Product_Name"], r["Current_Balance"], r["Minimum_Stock"],
            r["Stock_Deficit"], r["Recommended_Order_Qty"], r["Unit_Price"],
            r["Estimated_PO_Cost_INR"], r["Supplier"], r["Supplier_Contact"], r["Warehouse_Location"]
        ])
    style_table(ws, "DIT T04 — RECOMMENDED PURCHASE REQUISITION & REORDER LIST")
    wb.save(out_file)

def export_exception_report(anomalies: List[Dict[str, Any]], out_file: Path):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Exceptions_and_Anomalies"
    headers = ["Error_Type", "Record_Identifier", "Source_Data", "Failure_Reason"]
    ws.append(headers)
    for a in anomalies:
        ws.append([
            a.get("error_type", "ANOMALY"),
            a.get("id", "N/A"),
            str(a.get("raw", {})),
            a.get("reason", "Unknown validation error")
        ])
    style_table(ws, "DIT T04 — UNKNOWN CODES, NEGATIVE STOCK & AUDIT EXCEPTION REGISTER")
    wb.save(out_file)
