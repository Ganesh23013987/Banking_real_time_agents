"""Automated unit tests for BankMind Nexus (no API key or internet required)."""
import unittest
from unittest.mock import patch

from agents.supervisor import handle_request, detect_intent
from agents.credit_agent import calculate_emi, check_eligibility
from agents.risk_agent import analyze_risk
from tools.banking_api import get_customer, get_transactions


class BankingUseCaseTests(unittest.TestCase):
    """Tests for routing and the five core banking use cases."""

    def call_without_gemini(self, prompt):
        # Keep tests deterministic and avoid making paid/network API calls.
        with patch("agents.supervisor.improve_answer", side_effect=lambda _q, answer: (answer, "Test fallback")):
            return handle_request(prompt, "CUST1001")

    def test_01_account_balance(self):
        result = self.call_without_gemini("What is my account balance?")
        self.assertEqual(result["intent"], "balance")
        self.assertIn("78,500.00", result["answer"])
        self.assertIn("Customer Banking Agent", result["agents"])

    def test_02_recent_transactions(self):
        result = self.call_without_gemini("Show my recent transactions")
        self.assertEqual(result["intent"], "transactions")
        self.assertIn("Salary Credit", result["answer"])
        self.assertIn("Customer Banking Agent", result["agents"])

    def test_03_suspicious_transaction_detection(self):
        result = self.call_without_gemini("Check suspicious transactions")
        self.assertEqual(result["intent"], "transactions_and_risk")
        self.assertIn("Online Purchase", result["answer"])
        self.assertIn("Risk/Fraud Agent", result["agents"])

    def test_04_loan_eligibility(self):
        result = self.call_without_gemini("Am I eligible for a loan of 200000?")
        self.assertEqual(result["intent"], "credit")
        self.assertIn("200,000", result["answer"])
        self.assertIn("Credit/Loan Agent", result["agents"])

    def test_05_emi_calculation(self):
        result = self.call_without_gemini("Calculate EMI for 200000 over 24 months at 12%")
        self.assertEqual(result["intent"], "credit")
        self.assertIn("Estimated monthly EMI", result["answer"])
        self.assertIn("Credit/Loan Agent", result["agents"])

    def test_06_greeting_gets_a_natural_reply(self):
        result = self.call_without_gemini("hi")
        self.assertEqual(result["intent"], "greeting")
        self.assertIn("How can I help you today?", result["answer"])
        self.assertNotIn("Check my account balance", result["answer"])

    def test_07_emi_zero_interest(self):
        self.assertAlmostEqual(calculate_emi(1200, 0, 12), 100.0)

    def test_08_invalid_emi_rejected(self):
        with self.assertRaises(ValueError):
            calculate_emi(1000, 12, 0)

    def test_09_unknown_customer_rejected(self):
        with self.assertRaises(ValueError):
            get_customer("NOT_A_CUSTOMER")

    def test_10_demo_risk_flags_large_review_transaction(self):
        result = analyze_risk("CUST1001")
        flagged_descriptions = [x["description"] for x in result["data"]["flagged_transactions"]]
        self.assertIn("Online Purchase", flagged_descriptions)


if __name__ == "__main__":
    unittest.main(verbosity=2)
