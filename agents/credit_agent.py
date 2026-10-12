def calculate_emi(principal: float, annual_rate_percent: float, months: int) -> float:
    """Calculate EMI for a reducing-balance loan."""
    if principal <= 0:
        raise ValueError("Loan amount must be greater than zero.")
    if months <= 0:
        raise ValueError("Loan tenure must be at least one month.")
    if annual_rate_percent < 0:
        raise ValueError("Interest rate cannot be negative.")

    monthly_rate = annual_rate_percent / 12 / 100
    if monthly_rate == 0:
        return principal / months
    factor = (1 + monthly_rate) ** months
    return principal * monthly_rate * factor / (factor - 1)

def check_eligibility(customer_id: str, requested_amount: float = 200000) -> dict:
    """Illustrative eligibility estimate using fixed fictional demo income."""
    monthly_income = 45000
    existing_emi = 5000
    estimated_capacity = max(0, monthly_income * 0.40 - existing_emi)
    eligible = requested_amount > 0 and requested_amount <= 500000 and estimated_capacity > 0

    if eligible:
        message = (
            f"Illustrative assessment: a ₹{requested_amount:,.0f} request passes this demo's basic checks. "
            f"Assumed monthly income: ₹{monthly_income:,.0f}; assumed existing EMI: ₹{existing_emi:,.0f}. "
            "This is not a real credit decision or loan approval."
        )
    else:
        message = (
            f"Illustrative assessment: a ₹{requested_amount:,.0f} request does not pass this demo's basic amount checks. "
            "This is not a real credit decision."
        )

    return {
        "agent": "Credit/Loan Agent",
        "data": {
            "requested_amount": requested_amount,
            "monthly_income_assumption": monthly_income,
            "existing_emi_assumption": existing_emi,
            "estimated_monthly_capacity": estimated_capacity,
            "demo_check_passed": eligible
        },
        "message": message
    }
