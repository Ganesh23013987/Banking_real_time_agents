# BankMind Nexus – Simulated Multi-Agent Banking MVP

## Project Overview
BankMind Nexus is a simulated banking assistant developed using Python and Streamlit. It uses multiple specialized agents to handle customer banking queries, transaction risk analysis, and loan calculations. Optional Google Gemini integration helps generate natural-language responses.

## Features
- **Supervisor Agent:** Routes user queries to the appropriate specialist.
- **Customer Banking Agent:** Retrieves simulated account and transaction information.
- **Risk/Fraud Agent:** Flags potentially suspicious transactions using predefined rules.
- **Credit/Loan Agent:** Performs illustrative loan checks and calculates EMI.
- **Gemini Integration:** Optional AI-powered response generation.
- **Interactive Dashboard:** Displays banking information and transaction monitoring.
- **Agent Trace:** Helps demonstrate the agent workflow.
- **Fallback Mode:** Supports available deterministic responses when Gemini is unavailable.

## Technologies Used
- Python
- Streamlit
- Google Gemini API
- Pandas
- JSON and CSV
- Git and GitHub
- Render

## System Workflow
1. The user enters a banking query.
2. The Supervisor Agent identifies the request type.
3. The appropriate specialist agent processes the request.
4. Simulated banking tools provide the required data.
5. The application prepares a response.
6. Optional Gemini integration improves the response wording.
7. The result is displayed in the Streamlit interface.

## Project Structure
```text
BankMind-Nexus/
├── agents/
├── data/
├── tests/
├── tools/
├── utils/
├── app.py
├── requirements.txt
├── README.md
├── .env.example
└── .gitignore
```

## Installation and Setup

### 1. Clone the repository
```bash
git clone https://github.com/Ganesh23013987/Banking_real_time_agents.git
cd Banking_real_time_agents
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Gemini (Optional)

Set `GEMINI_API_KEY` and, if required by your code, `GEMINI_MODEL` in your local `.env` file. For deployment, configure these variables in Render's Environment settings.

Never upload your `.env` file or API key to GitHub.

### 4. Run the application
```bash
streamlit run app.py
```

Open the local URL displayed in the terminal, usually `http://localhost:8501`.

## Sample Queries
- What is my account balance?
- Show my recent transactions.
- Check whether any transaction looks suspicious.
- Am I eligible for a loan of ₹200000?
- Calculate EMI for ₹200000 over 24 months at 12% annual interest.


The project demonstrates multi-agent coordination in a simulated banking environment. It provides banking query handling, transaction monitoring using predefined rules, and loan EMI calculations through an interactive interface.

## Project Links
- **GitHub Repository:** https://github.com/Ganesh23013987/Banking_real_time_agents
- **Live Demo:** https://banking-real-time-agents.onrender.com

## Limitations
- Uses simulated banking data.
- Does not connect to real banking systems.
- Suspicious transaction flags are illustrative, not proof of fraud.
- Loan checks are demonstrations, not actual credit decisions.
- Gemini functionality depends on valid API configuration, model availability, and quota.

## Conclusion
BankMind Nexus demonstrates how a Supervisor Agent and specialized agents can work together to provide simulated banking assistance. The project combines Python, Streamlit, and optional Gemini integration in a modular and interactive application.
