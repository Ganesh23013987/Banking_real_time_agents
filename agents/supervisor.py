import re

from agents.customer_agent import handle_customer_request
from agents.risk_agent import analyze_risk
from agents.credit_agent import calculate_emi, check_eligibility
from utils.llm import improve_answer


def detect_intent(message: str) -> str:
    """Detect the user's intent using simple, explainable rules."""
    text = message.lower().strip()
    text = re.sub(r"[^\w\s₹%.-]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    # Banking requests take priority over greetings.
    if any(word in text for word in [
        "fraud", "suspicious", "risk", "unusual", "scam"
    ]):
        return "risk"

    if any(word in text for word in [
        "emi", "loan", "borrow", "eligible",
        "eligibility", "credit"
    ]):
        return "credit"

    if any(word in text for word in [
        "transaction", "spending", "spent", "payment", "debit"
    ]):
        return "transactions"

    if any(word in text for word in [
        "balance", "account", "customer", "profile", "money"
    ]):
        return "balance"

    # Recognize simple greetings before returning help.
    greeting_pattern = (
        r"^(hi|hello|hey|howdy|"
        r"good morning|good afternoon|good evening)"
        r"([.!?, ]|$)"
    )

    if re.match(greeting_pattern, text):
        return "greeting"

    return "help"


def _extract_amount(text: str, default: float = 200000) -> float:
    """Extract a monetary amount, supporting lakh notation."""
    lower = (
        text.lower()
        .replace(",", "")
        .replace("₹", "")
        .replace("rs.", "")
        .replace("rs ", "")
    )

    lakh = re.search(r"(\d+(?:\.\d+)?)\s*lakh\b", lower)
    if lakh:
        return float(lakh.group(1)) * 100000

    match = re.search(r"\b\d+(?:\.\d+)?\b", lower)
    return float(match.group()) if match else default


def _extract_months(text: str, default: int = 24) -> int:
    """Extract loan tenure in months or convert years to months."""
    lower = text.lower()

    match = re.search(r"\b(\d+)\s*(?:months?|mos?)\b", lower)
    if match:
        return int(match.group(1))

    year_match = re.search(r"\b(\d+)\s*years?\b", lower)
    if year_match:
        return int(year_match.group(1)) * 12

    return default


def _extract_rate(text: str, default: float = 12.0) -> float:
    """Extract an interest rate expressed as a percentage."""
    match = re.search(r"(\d+(?:\.\d+)?)\s*%", text)
    return float(match.group(1)) if match else default


def handle_request(message: str, customer_id: str) -> dict:
    """Route the request to the appropriate agent and format its answer."""
    lower = message.lower()
    results = []
    agents = []

    intent = detect_intent(message)

    # Greeting: respond naturally without showing the task-help list.
    if intent == "greeting":
        results.append(
            "Hi! 👋 Welcome to BankMind Nexus. "
            "How can I help you today? You can ask about your "
            "account balance, transactions, suspicious activity, "
            "loan eligibility, or EMI calculations."
        )
        agents.append("Supervisor Agent")

    # Run both specialists when the user asks for transactions and risk.
    elif (
        intent == "risk"
        and any(word in lower for word in [
            "transaction", "spending", "spent", "payment", "debit"
        ])
    ):
        customer_result = handle_customer_request(
            customer_id, "transactions"
        )
        risk_result = analyze_risk(customer_id)

        results.extend([
            customer_result["message"],
            risk_result["message"]
        ])
        agents.extend([
            customer_result["agent"],
            risk_result["agent"]
        ])
        intent = "transactions_and_risk"

    elif intent == "balance":
        result = handle_customer_request(customer_id, "balance")
        results.append(result["message"])
        agents.append(result["agent"])

    elif intent == "transactions":
        result = handle_customer_request(customer_id, "transactions")
        results.append(result["message"])
        agents.append(result["agent"])

    elif intent == "risk":
        result = analyze_risk(customer_id)
        results.append(result["message"])
        agents.append(result["agent"])

    elif intent == "credit":
        if "emi" in lower:
            amount = _extract_amount(message)
            months = _extract_months(message)
            rate = _extract_rate(message)

            if amount <= 0:
                results.append("Please enter a loan amount greater than zero.")
            elif months <= 0:
                results.append("Please enter a tenure greater than zero months.")
            elif rate < 0:
                results.append("Please enter a non-negative annual interest rate.")
            else:
                emi = calculate_emi(amount, rate, months)

                results.append(
                    f"Estimated monthly EMI: ₹{emi:,.2f}\n"
                    f"Loan amount: ₹{amount:,.2f}; "
                    f"annual interest: {rate:g}%; "
                    f"tenure: {months} months.\n"
                    "This is an illustrative calculation, not a lender quote."
                )

            agents.append("Credit/Loan Agent")

        else:
            amount = _extract_amount(message)
            result = check_eligibility(customer_id, amount)
            results.append(result["message"])
            agents.append(result["agent"])

    else:
        results.append(
            "I can help you with these banking tasks:\n"
            "- Check your account balance\n"
            "- Show recent transactions\n"
            "- Check suspicious transactions\n"
            "- Check loan eligibility\n"
            "- Calculate EMI\n\n"
            "Try asking a banking question in your own words."
        )
        agents.append("Supervisor Agent")

    raw_answer = "\n\n".join(results)

    # Gemini may rewrite the response but must preserve verified facts.
    answer, method = improve_answer(message, raw_answer)

    return {
        "answer": answer,
        "agents": agents,
        "method": method,
        "intent": intent
    }
