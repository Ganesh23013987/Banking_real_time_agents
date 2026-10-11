
from utils.llm import generate_gemini_response

try:
    answer = generate_gemini_response(
        "Reply with exactly: Gemini connection successful."
    )

    print("\nSUCCESS:")
    print(answer)

except Exception as exc:
    print("\nGEMINI CONNECTION FAILED")
    print(type(exc).__name__)
    print(str(exc))
