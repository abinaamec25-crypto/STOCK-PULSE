from typing import Dict, Any, List

def calculate_stock_balance(opening: float, total_in: float, total_out: float) -> float:
    """Balance = Opening Stock + Stock IN - Stock OUT"""
    return round(opening + total_in - total_out, 2)

def evaluate_reorder(current_balance: float, min_stock: float) -> str:
    """Mentor Rule: Current Stock < Minimum Stock -> Reorder YES"""
    return "YES" if current_balance < min_stock else "NO"

def classify_stock_health(balance: float, min_stock: float) -> str:
    if balance < 0:
        return "NEGATIVE STOCK (CRITICAL)"
    if balance == 0:
        return "OUT OF STOCK"
    if balance <= min_stock * 0.25:
        return "CRITICAL BUFFER"
    if balance < min_stock:
        return "LOW STOCK"
    if balance > min_stock * 3.0:
        return "OVERSTOCKED"
    return "HEALTHY"
