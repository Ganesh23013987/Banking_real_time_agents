from tools.banking_api import get_customer, get_transactions

def handle_customer_request(customer_id: str, intent: str) -> dict:
    """Handle account and transaction questions using mock banking tools."""
    customer = get_customer(customer_id)

    if intent == "balance":
        return {
            "agent": "Customer Banking Agent",
            "data": {"name": customer["name"], "balance": customer["balance"]},
            "message": f"{customer['name']}'s simulated available balance is ₹{customer['balance']:,.2f}."
        }

    transactions = get_transactions(customer_id)
    if intent == "transactions":
        recent = transactions[:5]
        lines = [
            f"- {t['date']}: {t['description']} — ₹{t['amount']:,.2f} ({t['type']})"
            for t in recent
        ]
        return {
            "agent": "Customer Banking Agent",
            "data": {"transactions": recent},
            "message": "Here are the five most recent simulated transactions:\n" + "\n".join(lines)
        }

    debits = sum(t["amount"] for t in transactions if t["type"] == "debit")
    return {
        "agent": "Customer Banking Agent",
        "data": {"customer": customer, "transactions": transactions},
        "message": f"Customer information and {len(transactions)} transactions retrieved. Total debits in the sample data: ₹{debits:,.2f}."
    }
