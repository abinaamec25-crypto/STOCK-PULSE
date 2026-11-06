import re
from typing import Dict, Any, Tuple, Set

def normalize_column_name(raw_name: Any, is_tx: bool = False) -> str:
    s = re.sub(r'[^a-zA-Z0-9]', '', str(raw_name or "")).lower()

    if any(k in s for k in ["productid", "itemid", "itemcode", "partno", "partnum", "skucode", "skuid", "materialcode", "artnr"]):
        return "Product_ID"
    if s in ["sku", "code", "id", "part", "item"]:
        return "Product_ID"

    if is_tx:
        if any(k in s for k in ["txnid", "transactionid", "transid", "refid", "entryno", "voucherno"]):
            return "Transaction_ID"
        if any(k in s for k in ["txndate", "transactiondate", "date", "entrydate", "movementdate"]):
            return "Transaction_Date"
        if any(k in s for k in ["txntype", "transactiontype", "movement", "action", "type", "inout"]):
            return "Transaction_Type"
        if any(k in s for k in ["qty", "quantity", "units", "count", "pieces", "volume"]):
            return "Quantity"
        if any(k in s for k in ["refno", "referenceno", "pono", "invoiceno", "docno", "challanno"]):
            return "Reference_No"
        if any(k in s for k in ["remarks", "notes", "department", "deptremarks", "reason", "purpose"]):
            return "Department_Remarks"

    # Master attributes
    if any(k in s for k in ["productname", "itemname", "description", "partname", "materialdesc", "itemdesc", "productdesc"]):
        return "Product_Name"
    if s in ["name", "title", "product", "desc", "details"]:
        return "Product_Name"

    if any(k in s for k in ["minstock", "minimumstock", "safetystock", "reorderlevel", "minqty", "reorderpoint", "threshold", "buffer"]):
        return "Minimum_Stock"
    if s in ["min", "safety", "reorder"]:
        return "Minimum_Stock"

    if any(k in s for k in ["reorderqty", "reorderquantity", "orderqty", "orderquantity", "lotsize", "batchsize", "poqty"]):
        return "Reorder_Quantity"

    if any(k in s for k in ["openingstock", "initialstock", "openingbalance", "openingqty", "startstock"]):
        return "Opening_Stock"

    if any(k in s for k in ["currentstock", "onhand", "available", "instock", "stockqty", "balance", "physicalstock", "inventory"]):
        return "Current_Stock"
    if any(k in s for k in ["stock", "qty", "quantity", "count", "units"]):
        return "Current_Stock"

    if any(k in s for k in ["category", "dept", "department", "group", "productgroup", "type", "class", "segment"]):
        return "Category"

    if any(k in s for k in ["unitprice", "price", "rate", "cost", "unitcost", "mrp", "amount"]):
        return "Unit_Price"

    if any(k in s for k in ["email", "suppliercontact", "vendorcontact", "phone", "contactmail"]):
        return "Supplier_Contact"

    if any(k in s for k in ["supplier", "vendor", "manufacturer", "distributor", "source"]):
        return "Supplier"

    if any(k in s for k in ["location", "warehouse", "bay", "bin", "shelf", "rack", "store"]):
        return "Warehouse_Location"

    return str(raw_name).strip()


def sanitize_numeric(value: Any, default: float = 0.0) -> float:
    if value is None:
        return default
    if isinstance(value, (int, float)):
        return float(value)
    cleaned = re.sub(r'[^0-9.-]', '', str(value).strip())
    try:
        return float(cleaned)
    except (ValueError, TypeError):
        return default


def validate_and_sanitize_master_record(rec: Dict[str, Any], seen_ids: Set[str], fallback_idx: int) -> Tuple[bool, str, Dict[str, Any]]:
    raw_id = str(rec.get("Product_ID") or "").strip()
    if not raw_id or raw_id.lower() in ["none", "nan", "null"]:
        raw_id = f"SKU-{fallback_idx:04d}"

    if raw_id in seen_ids:
        return False, f"Duplicate Record: Product_ID '{raw_id}' already processed", {}

    raw_name = str(rec.get("Product_Name") or f"Item {raw_id}").strip()
    cat = str(rec.get("Category") or "General Inventory").strip()

    opening = sanitize_numeric(rec.get("Opening_Stock") or rec.get("Current_Stock"), 0.0)
    current = sanitize_numeric(rec.get("Current_Stock"), opening)
    min_stock = sanitize_numeric(rec.get("Minimum_Stock"), max(10.0, round(current * 0.25, 1)))
    reorder_qty = sanitize_numeric(rec.get("Reorder_Quantity"), max(20.0, round(min_stock * 2.0, 1)))
    unit_price = sanitize_numeric(rec.get("Unit_Price"), 150.0)

    if opening < 0:
        return False, f"Negative Opening Stock Disallowed: {opening}", {}

    supplier = str(rec.get("Supplier") or "Standard Approved Vendor").strip()
    contact = str(rec.get("Supplier_Contact") or "orders@vendor-spares.com").strip()
    if "@" not in contact or "." not in contact:
        contact = "orders@vendor-spares.com"
    loc = str(rec.get("Warehouse_Location") or "Main Warehouse Bay A-1").strip()

    return True, "Valid", {
        "Product_ID": raw_id,
        "Product_Name": raw_name,
        "Category": cat,
        "Opening_Stock": opening,
        "Current_Stock": current,
        "Minimum_Stock": min_stock,
        "Reorder_Quantity": reorder_qty,
        "Unit_Price": unit_price,
        "Supplier": supplier,
        "Supplier_Contact": contact,
        "Warehouse_Location": loc
    }


def validate_and_sanitize_transaction(tx: Dict[str, Any], master_ids: Set[str], fallback_idx: int) -> Tuple[bool, str, Dict[str, Any]]:
    tx_id = str(tx.get("Transaction_ID") or f"TXN-{fallback_idx:04d}").strip()
    pid = str(tx.get("Product_ID") or "").strip()

    if not pid or pid not in master_ids:
        return False, f"Unknown Product Code '{pid}' (Not in Master Catalog)", {}

    qty = sanitize_numeric(tx.get("Quantity"), 0.0)
    if qty <= 0:
        return False, f"Invalid Quantity ({qty}): Must be positive (>0)", {}

    raw_type = str(tx.get("Transaction_Type") or "STOCK_OUT").upper().strip()
    if any(k in raw_type for k in ["IN", "RECEIPT", "RESTOCK", "PURCHASE", "RETURN"]):
        tx_type = "STOCK_IN"
    else:
        tx_type = "STOCK_OUT"

    date_str = str(tx.get("Transaction_Date") or "2026-10-31").strip()
    ref_no = str(tx.get("Reference_No") or f"REF-{fallback_idx:04d}").strip()
    remarks = str(tx.get("Department_Remarks") or "Routine warehouse movement").strip()

    return True, "Valid", {
        "Transaction_ID": tx_id,
        "Product_ID": pid,
        "Transaction_Date": date_str,
        "Transaction_Type": tx_type,
        "Quantity": qty,
        "Reference_No": ref_no,
        "Department_Remarks": remarks
    }
