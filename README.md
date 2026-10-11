# Banking_real_time_agents

# BankMind Nexus — Simulated Multi-Agent Banking MVP

A beginner-friendly Python/Streamlit project demonstrating how a supervisor coordinates three specialist agents in a fictional banking environment.

## Features

- **Supervisor Agent** routes a customer's natural-language request.
- **Customer Banking Agent** retrieves mock customer and transaction information.
- **Risk/Fraud Agent** flags transactions using explainable demo rules.
- **Credit/Loan Agent** estimates loan checks and calculates EMI.
- **Simulated banking tools** act like simple banking API endpoints.
- **Gemini integration** optionally improves the wording of grounded results.
- **Fallback mode** works without an API key.
- **Streamlit UI** provides dashboard, chat, transaction radar and agent trace.

> Safety note: This is an educational simulation. It does not connect to a bank, use real customer data, approve loans, or prove fraud.

## Requirements

- Python 3.10 or newer
- Internet connection only if you want to call Gemini
- Gemini API key is optional

## Run on Windows

Open a terminal in this folder and run:

```bash
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
```

Optional Gemini setup:

1. Copy `.env.example` to `.env`.
2. Add your key to `GEMINI_API_KEY`.
3. Check that `GEMINI_MODEL` is a model available to your API key.

Start the app:

```bash
streamlit run app.py
```

The app opens in your browser, usually at `http://localhost:8501`.

## Demo questions

- What is my account balance?
- Show my recent transactions.
- Check whether any transaction looks suspicious.
- Am I eligible for a loan of ₹200000?
- Calculate EMI for ₹200000 over 24 months at 12% annual interest.

## Architecture

```text
User
  |
  v
Streamlit UI
  |
  v
Supervisor Agent (intent routing)
  |-------------|----------------|
  v             v                v
Customer Agent  Risk Agent       Credit Agent
  |             |                |
  +-------------+----------------+
                |
                v
      Simulated Banking Tools
                |
                v
       Grounded result returned
                |
                v
   Optional Gemini response wording
```

## Explanation

"I built BankMind Nexus, a simulated banking application that demonstrates multi-agent collaboration. The user asks a question in a Streamlit chat interface. A supervisor uses simple intent-routing rules to decide which specialist should handle it. The Customer Agent retrieves account and transaction data from mock banking tools, the Risk Agent flags transactions using transparent rules, and the Credit Agent estimates loan eligibility and calculates EMI. An optional Gemini integration rewrites the verified result in natural language without being allowed to invent banking facts. I also added a dashboard and an agent trace page so the flow can be demonstrated. All data is fictional and no real banking API is connected."

## Important design choices

- Routing is intentionally simple and explainable; this is suitable for an MVP interview demo.
- Risk scoring is a demo indicator, not a trained fraud model or production fraud probability.
- Loan eligibility is illustrative, not a real credit decision.
- If the Gemini key is absent or the API call fails, deterministic application results are still returned.
- Do not commit `.env` or any API key to GitHub.

## Upload to GitHub

Create a new empty repository on GitHub, then run these commands in the project directory:

```bash
git init
git add .
git commit -m "Build BankMind Nexus multi-agent banking MVP"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/BankMind-Nexus.git
git push -u origin main
```

Replace `YOUR_USERNAME` with your GitHub username. Confirm `.env` is not staged before pushing.
