import unittest
import sys
from pathlib import Path

pkg_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(pkg_root / "src"))

from validation import validate_master_record, validate_transaction_record
from business_rules import calculate_stock_balance, evaluate_reorder, classify_stock_health

class TestDIT04Inventory(unittest.TestCase):
    def test_stock_balance_calculation(self):
        # Balance = Opening + In - Out
        balance = calculate_stock_balance(50, 20, 25)
        self.assertEqual(balance, 45.0)

    def test_reorder_condition(self):
        # Current Stock < Minimum Stock -> YES
        self.assertEqual(evaluate_reorder(15, 25), "YES")
        self.assertEqual(evaluate_reorder(30, 25), "NO")

    def test_negative_stock_health(self):
        # Negative balance check
        status = classify_stock_health(-5, 20)
        self.assertIn("NEGATIVE", status)

    def test_unknown_product_code_rejection(self):
        master_ids = {"PRD-1001", "PRD-1002"}
        raw_tx = {"Transaction_ID": "TX-1", "Product_ID": "PRD-9999", "Quantity": 10, "Transaction_Type": "STOCK_OUT"}
        ok, reason, _ = validate_transaction_record(raw_tx, master_ids)
        self.assertFalse(ok)
        self.assertIn("Unknown Product Code", reason)

    def test_valid_transaction(self):
        master_ids = {"PRD-1001"}
        raw_tx = {"Transaction_ID": "TX-1", "Product_ID": "PRD-1001", "Quantity": 15, "Transaction_Type": "STOCK_IN"}
        ok, _, clean = validate_transaction_record(raw_tx, master_ids)
        self.assertTrue(ok)
        self.assertEqual(clean["Quantity"], 15.0)

if __name__ == "__main__":
    unittest.main()
