
import streamlit as st
import pandas as pd
import plotly.express as px
import hashlib
import hmac
import json
import secrets
import re
from pathlib import Path

from tools.banking_api import get_customer, get_transactions
from agents.supervisor import handle_request


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="BankMind Nexus",
    page_icon="🏦",
    layout="wide",
)

st.markdown("""
<style>
.block-container {
    padding-top: 1.2rem;
    padding-bottom: 2rem;
}
.hero {
    padding: 1.3rem;
    border-radius: 16px;
    background: linear-gradient(120deg, #10233f, #176b87);
    color: white;
    margin-bottom: 1rem;
}
div.stButton > button {
    border-radius: 10px;
    min-height: 42px;
}
</style>
""", unsafe_allow_html=True)


# =========================================================
# PATHS AND DEMO AUTHENTICATION
# =========================================================

BASE_DIR = Path(__file__).resolve().parent
USERS_FILE = BASE_DIR / "data" / "users.json"
USERS_FILE.parent.mkdir(parents=True, exist_ok=True)


def load_users():
    if not USERS_FILE.exists():
        return {}

    try:
        return json.loads(
            USERS_FILE.read_text(encoding="utf-8")
        )
    except (OSError, json.JSONDecodeError):
        return {}


def save_users(users):
    USERS_FILE.write_text(
        json.dumps(users, indent=2),
        encoding="utf-8",
    )


def hash_password(password, salt=None):
    salt = salt or secrets.token_bytes(16)

    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        310000,
    )

    return salt.hex(), digest.hex()


def create_account(name, email, password):
    name = name.strip()
    email = email.strip().lower()

    if len(name) < 2:
        return False, "Please enter your full name."

    if "@" not in email or "." not in email.split("@")[-1]:
        return False, "Please enter a valid email address."

    if len(password) < 8:
        return False, "Password must contain at least 8 characters."

    users = load_users()

    if email in users:
        return False, "Account already exists. Please sign in."

    salt, digest = hash_password(password)

    users[email] = {
        "name": name,
        "salt": salt,
        "password_hash": digest,
    }

    save_users(users)

    return True, "Account created. You can now sign in."


def sign_in(email, password):
    email = email.strip().lower()
    user = load_users().get(email)

    if not user:
        return None

    _, digest = hash_password(
        password,
        bytes.fromhex(user["salt"]),
    )

    if hmac.compare_digest(digest, user["password_hash"]):
        return {
            "name": user["name"],
            "email": email,
        }

    return None


# =========================================================
# SESSION STATE
# Initialize workspace BEFORE creating the radio widget.
# =========================================================

defaults = {
    "user": None,
    "messages": [],
    "agent_trace": [],
    "pending_prompt": None,
    "workspace": "Mission Control",
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# =========================================================
# CALLBACKS
# =========================================================

def open_banking_assistant(task):
    # This callback runs before Streamlit reruns the page.
    st.session_state.pending_prompt = task
    st.session_state.workspace = "AI Banking Assistant"


def sign_out():
    st.session_state.user = None
    st.session_state.messages = []
    st.session_state.agent_trace = []
    st.session_state.pending_prompt = None
    st.session_state.workspace = "Mission Control"


# =========================================================
# FAST LOCAL RESPONSES
# These avoid unnecessary Gemini API requests.
# =========================================================

def fast_local_response(prompt, customer, transactions):
    text = prompt.strip().lower()
    normalized = re.sub(r"[^\w\s]", "", text)

    greetings = {
        "hi", "hello", "hey", "good morning",
        "good afternoon", "good evening",
        "hi there", "hello there",
    }

    if normalized in greetings:
        return {
            "answer": (
                "Hi! 👋 Welcome to BankMind Nexus. "
                "I can help you check your demo account balance, "
                "review transactions, flag suspicious activity, "
                "and calculate loan EMIs. What would you like to do?"
            ),
            "agents": ["Supervisor Agent"],
            "intent": "greeting",
            "method": "Instant local response",
        }

    if (
        "thank you" in text
        or "thanks" in text
        or normalized in {"thank", "thx"}
    ):
        return {
            "answer": "You're welcome! 😊 What else can I help you with?",
            "agents": ["Supervisor Agent"],
            "intent": "thanks",
            "method": "Instant local response",
        }

    # Balance questions are answered directly from demo data.
    if (
        "balance" in text
        and not any(word in text for word in [
            "loan", "credit", "eligibility"
        ])
    ):
        return {
            "answer": (
                f"Your simulated account balance is "
                f"₹{float(customer['balance']):,.2f}."
            ),
            "agents": ["Customer Banking Agent"],
            "intent": "balance",
            "method": "Instant local banking tool",
        }

    # Recent transaction questions are answered locally.
    transaction_phrases = [
        "recent transaction",
        "show transactions",
        "my transactions",
        "transaction history",
        "last transaction",
    ]

    if any(phrase in text for phrase in transaction_phrases):
        if not transactions:
            answer = "There are no demo transactions available."
        else:
            lines = []

            for tx in transactions[:5]:
                date = tx.get("date", "Unknown date")
                description = tx.get(
                    "description",
                    tx.get("merchant", "Transaction"),
                )
                amount = float(tx.get("amount", 0))
                tx_type = str(tx.get("type", "")).upper()
                status = tx.get("status", "Unknown")

                lines.append(
                    f"- **{date}** — {description}: "
                    f"₹{amount:,.2f} ({tx_type}), status: {status}"
                )

            answer = (
                "**Your latest demo transactions:**\n\n"
                + "\n".join(lines)
            )

        return {
            "answer": answer,
            "agents": ["Customer Banking Agent"],
            "intent": "transactions",
            "method": "Instant local banking tool",
        }

    return None


# =========================================================
# SIGN IN AND CREATE ACCOUNT
# =========================================================

if st.session_state.user is None:

    st.markdown("""
    <div class="hero">
        <h1>🏦 BankMind Nexus</h1>
        <p>
            Simulated banking with intelligent multi-agent automation.
        </p>
    </div>
    """, unsafe_allow_html=True)

    signin_tab, signup_tab = st.tabs(
        ["Sign In", "Create Account"]
    )

    with signin_tab:

        with st.form("signin_form"):

            email = st.text_input("Email address")
            password = st.text_input(
                "Password",
                type="password",
            )

            submitted = st.form_submit_button(
                "Sign In",
                type="primary",
                use_container_width=True,
            )

        if submitted:
            logged_in_user = sign_in(email, password)

            if logged_in_user:
                st.session_state.user = logged_in_user
                st.session_state.messages = []
                st.session_state.agent_trace = []
                st.session_state.pending_prompt = None
                st.session_state.workspace = "Mission Control"
                st.rerun()
            else:
                st.error("Incorrect email or password.")

    with signup_tab:

        with st.form("signup_form"):

            name = st.text_input("Full name")
            new_email = st.text_input("Email address")
            new_password = st.text_input(
                "Create password",
                type="password",
            )
            confirm_password = st.text_input(
                "Confirm password",
                type="password",
            )

            submitted = st.form_submit_button(
                "Create Account",
                type="primary",
                use_container_width=True,
            )

        if submitted:

            if new_password != confirm_password:
                st.error("Passwords do not match.")
            else:
                ok, message = create_account(
                    name,
                    new_email,
                    new_password,
                )

                if ok:
                    st.success(message)
                else:
                    st.error(message)

    st.caption(
        "Educational simulation only. Never use real banking credentials."
    )

    st.stop()


# =========================================================
# LOAD SIMULATED BANKING DATA
# =========================================================

user = st.session_state.user

customer = get_customer("CUST1001")
transactions = get_transactions("CUST1001")

if not customer:
    st.error("Demo customer CUST1001 was not found.")
    st.stop()

df = pd.DataFrame(transactions)


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.title("🏦 BankMind Nexus")
    st.caption("MULTI-AGENT BANKING MVP")

    st.success(f"Signed in as {user['name']}")

    page = st.radio(
        "Workspace",
        [
            "Mission Control",
            "AI Banking Assistant",
            "Transaction Radar",
            "Agent Trace",
        ],
        key="workspace",
    )

    st.divider()

    st.markdown("### Agent team")
    st.write("🧭 Supervisor / Orchestrator")
    st.write("👤 Customer Banking Agent")
    st.write("🛡️ Risk / Fraud Agent")
    st.write("💳 Credit / Loan Agent")

    st.info("All account and transaction data is simulated.")

    st.button(
        "Sign Out",
        use_container_width=True,
        on_click=sign_out,
    )


# =========================================================
# MISSION CONTROL
# =========================================================

if page == "Mission Control":

    st.markdown("""
    <div class="hero">
        <h1>Mission Control</h1>
        <p>
            One supervisor. Three specialist agents.
            Faster local answers with optional Gemini integration.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.write(f"Welcome, **{user['name']}**.")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Demo Balance",
        f"₹{float(customer['balance']):,.2f}",
    )

    col2.metric("Transactions", len(df))
    col3.metric("Specialist Agents", "3")

    left, right = st.columns([1.4, 1])

    with left:

        st.subheader("Recent Transactions")

        if not df.empty:

            preferred = [
                "date", "description", "category",
                "amount", "type", "status",
            ]

            columns = [
                col for col in preferred if col in df.columns
            ]

            st.dataframe(
                df[columns],
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No transactions available.")

    with right:

        st.subheader("Spending by Category")

        required = {"type", "category", "amount"}

        if not df.empty and required.issubset(df.columns):

            # Handle either debit or Debit in the source data.
            debit_rows = df[
                df["type"].astype(str).str.lower() == "debit"
            ]

            expenses = (
                debit_rows.groupby("category", as_index=False)["amount"]
                .sum()
            )

            if not expenses.empty:

                fig = px.pie(
                    expenses,
                    names="category",
                    values="amount",
                    hole=0.45,
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True,
                )
            else:
                st.info("No debit transactions found.")
        else:
            st.info("Transaction category data is unavailable.")

    st.subheader("Quick Banking Tasks")

    tasks = [
        "What is my account balance?",
        "Show my recent transactions",
        "Check my transactions and flag anything suspicious",
        "Am I eligible for a loan of ₹200000?",
        "Calculate EMI for ₹200000 over 24 months at 12% annual interest",
    ]

    cols = st.columns(5)

    for i, task in enumerate(tasks):

        with cols[i]:

            st.button(
                task,
                key=f"task_{i}",
                use_container_width=True,
                on_click=open_banking_assistant,
                args=(task,),
            )


# =========================================================
# AI BANKING ASSISTANT
# =========================================================

elif page == "AI Banking Assistant":

    st.title("💬 AI Banking Assistant")

    st.caption(
        "Greetings, balance and recent transactions use fast local "
        "responses. Other requests are routed to your specialist agents."
    )

    for message in st.session_state.messages:

        with st.chat_message(message["role"]):

            st.markdown(message["content"])

            if message.get("agents"):
                st.caption(
                    "Agent route: "
                    + " → ".join(message["agents"])
                )

            if message.get("method"):
                st.caption(
                    "Response method: " + message["method"]
                )

    # Consume a queued quick task.
    prompt = st.session_state.pending_prompt
    st.session_state.pending_prompt = None

    typed_prompt = st.chat_input(
        "Ask about balance, transactions, risk, loans or EMI..."
    )

    if typed_prompt:
        prompt = typed_prompt

    if prompt:

        st.session_state.messages.append({
            "role": "user",
            "content": prompt,
        })

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):

            try:

                # First: fast local responses without Gemini.
                result = fast_local_response(
                    prompt,
                    customer,
                    transactions,
                )

                # Second: use the existing supervisor for other requests.
                if result is None:

                    with st.spinner("Checking your banking request..."):

                        result = handle_request(
                            prompt,
                            customer["customer_id"],
                        )

                    if not isinstance(result, dict):
                        raise ValueError(
                            "Supervisor returned an invalid response."
                        )

                answer = str(
                    result.get(
                        "answer",
                        "Sorry, I could not generate a response.",
                    )
                )

                agents = result.get("agents", [])
                if isinstance(agents, str):
                    agents = [agents]

                method = result.get(
                    "method",
                    "Application response",
                )

                intent = result.get(
                    "intent",
                    "not reported",
                )

                st.markdown(answer)

                if agents:
                    st.caption(
                        "Agent route: " + " → ".join(agents)
                    )

                st.caption("Response method: " + str(method))

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "agents": agents,
                    "method": method,
                })

                st.session_state.agent_trace.append({
                    "request": prompt,
                    "intent": intent,
                    "agents": " → ".join(agents),
                    "method": method,
                })

            except Exception as error:

                error_text = str(error)

                if (
                    "429" in error_text
                    or "RESOURCE_EXHAUSTED" in error_text
                    or "quota" in error_text.lower()
                ):
                    answer = (
                        "⚠️ Gemini's API quota is exhausted. "
                        "Fast local responses for greetings, balance "
                        "and recent transactions remain available. "
                        "For this request, please retry when the Gemini "
                        "quota resets or after resolving your quota limit."
                    )
                else:
                    answer = (
                        "I couldn't process that request. "
                        "Please check the terminal for the detailed error."
                    )

                st.warning(answer)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "agents": ["Supervisor Agent"],
                    "method": "Fallback response",
                })


# =========================================================
# TRANSACTION RADAR
# =========================================================

elif page == "Transaction Radar":

    st.title("📊 Transaction Radar")

    if df.empty:
        st.info("No demo transactions available.")
    elif "category" in df.columns:

        categories = sorted(
            df["category"].dropna().unique().tolist()
        )

        category = st.selectbox(
            "Filter by category",
            ["All"] + categories,
        )

        filtered = (
            df if category == "All"
            else df[df["category"] == category]
        )

        st.dataframe(
            filtered,
            use_container_width=True,
            hide_index=True,
        )

        if {"type", "amount"}.issubset(filtered.columns):

            debit_total = filtered.loc[
                filtered["type"].astype(str).str.lower() == "debit",
                "amount",
            ].sum()

            credit_total = filtered.loc[
                filtered["type"].astype(str).str.lower() == "credit",
                "amount",
            ].sum()

            c1, c2 = st.columns(2)

            c1.metric("Total Debits", f"₹{debit_total:,.2f}")
            c2.metric("Total Credits", f"₹{credit_total:,.2f}")

    else:
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
        )


# =========================================================
# AGENT TRACE
# =========================================================

elif page == "Agent Trace":

    st.title("🧭 Agent Execution Trace")

    if st.session_state.agent_trace:

        st.dataframe(
            pd.DataFrame(st.session_state.agent_trace),
            use_container_width=True,
            hide_index=True,
        )

    else:
        st.info("No agent requests recorded yet.")

    st.divider()

    st.markdown("""
    ### How the application works

    1. The Streamlit interface receives the user's question.
    2. Fast local handlers answer common questions.
    3. The supervisor routes other requests to specialist agents.
    4. Banking tools retrieve simulated account and transaction data.
    5. Gemini can provide AI-generated responses when its API is available.
    """)

    st.warning(
        "Educational simulation only. Transaction flags and loan "
        "eligibility are not real banking decisions."
    )
