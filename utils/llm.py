"""Optional Gemini integration. The app still works with deterministic answers if no key is set."""
import os
from dotenv import load_dotenv

load_dotenv()

def improve_answer(user_message: str, grounded_answer: str) -> tuple[str, str]:
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    model_name = os.getenv("GEMINI_MODEL", "gemini-3.8-flash").strip()

    if not api_key:
        return grounded_answer, "Rule-based fallback (no GEMINI_API_KEY configured)"

    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        prompt = f"""
You are a helpful assistant for a simulated banking application.
Rewrite the supplied result in clear, concise language for the customer.
IMPORTANT:
- Treat the supplied result as the only source of banking facts.
- Do not invent balances, transactions, interest rates, eligibility, or approvals.
- Keep all amounts and caveats accurate.
- This is fictional demo data, not a real bank.
User request: {user_message}
Verified application result:
{grounded_answer}
"""
        response = client.models.generate_content(
            model=model_name,
            contents=prompt
        )
        answer = getattr(response, "text", None)
        if answer and answer.strip():
            return answer.strip(), f"Gemini LLM ({model_name})"
        return grounded_answer, "Rule-based fallback (empty LLM response)"
    except Exception:
        # Do not crash the banking demo if the hosted LLM is unavailable.
        return grounded_answer, "Rule-based fallback (LLM unavailable; check key/model/network)"
