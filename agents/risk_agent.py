from tools.banking_api import get_transactions

def analyze_risk(customer_id: str) -> dict:
    """Apply simple, explainable rules to fictional transaction data."""
    transactions = get_transactions(customer_id)
    flagged = []

    for transaction in transactions:
        reasons = []
        if transaction["type"] == "debit" and transaction["amount"] >= 20000:
            reasons.append("large debit (₹20,000 or more)")
        if transaction.get("status", "").lower() == "review":
            reasons.append("transaction marked for review")
        if reasons:
            flagged.append({
                "date": transaction["date"],
                "description": transaction["description"],
                "amount": transaction["amount"],
                "reasons": reasons
            })

    if flagged:
        lines = [
            f"- {item['date']} — {item['description']} — ₹{item['amount']:,.2f}: {', '.join(item['reasons'])}"
            for item in flagged
        ]
        message = "I found transaction(s) matching the demo risk rules:\n" + "\n".join(lines)
        message += "\n\nThese are rule-based risk indicators, not proof of fraud."
    else:
        message = "No transactions matched the configured demo risk rules. This does not guarantee that every transaction is safe."

    # This is a transparent demo score, not a production fraud probability.
    score = min(100, len(flagged) * 25)
    return {
        "agent": "Risk/Fraud Agent",
        "data": {"flagged_transactions": flagged, "demo_risk_score": score},
        "message": f"Demo risk score: {score}/100.\n{message}"
    }
