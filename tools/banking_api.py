"""Mock banking APIs. All records are fictional and stored locally for the demo."""

CUSTOMERS = {
    "CUST1001": {
        "customer_id": "CUST1001",
        "name": "Arun Kumar (Demo Customer)",
        "balance": 78500.00,
        "monthly_income": 45000.00
    }
}

TRANSACTIONS = [
    {"date": "2026-10-10", "description": "Salary Credit", "category": "Income", "amount": 45000.00, "type": "credit", "status": "normal"},
    {"date": "2026-10-09", "description": "Groceries", "category": "Shopping", "amount": 2450.00, "type": "debit", "status": "normal"},
    {"date": "2026-10-08", "description": "Electricity Bill", "category": "Utilities", "amount": 1800.00, "type": "debit", "status": "normal"},
    {"date": "2026-10-07", "description": "Online Purchase", "category": "Shopping", "amount": 24500.00, "type": "debit", "status": "review"},
    {"date": "2026-10-06", "description": "Restaurant", "category": "Food", "amount": 950.00, "type": "debit", "status": "normal"},
    {"date": "2026-10-05", "description": "ATM Withdrawal", "category": "Cash", "amount": 5000.00, "type": "debit", "status": "normal"},
    {"date": "2026-10-04", "description": "Fuel", "category": "Transport", "amount": 2200.00, "type": "debit", "status": "normal"},
    {"date": "2026-10-03", "description": "Mobile Recharge", "category": "Utilities", "amount": 399.00, "type": "debit", "status": "normal"},
]

def get_customer(customer_id: str) -> dict:
    """Simulate GET /customers/{customer_id}."""
    if customer_id not in CUSTOMERS:
        raise ValueError(f"Customer {customer_id} was not found in the demo data.")
    return dict(CUSTOMERS[customer_id])

def get_transactions(customer_id: str) -> list:
    """Simulate GET /customers/{customer_id}/transactions."""
    if customer_id not in CUSTOMERS:
        raise ValueError(f"Customer {customer_id} was not found in the demo data.")
    # Return a copy so UI code cannot accidentally mutate the source records.
    return [dict(transaction) for transaction in TRANSACTIONS]
