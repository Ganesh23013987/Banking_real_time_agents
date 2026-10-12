"""Simple local demo authentication for BankMind Nexus.

For learning/demo use only. Production apps should use a dedicated identity provider,
HTTPS, rate limiting, secure session management, and a database.
"""
import hashlib
import hmac
import json
import os
import secrets
from pathlib import Path

USERS_FILE = Path(__file__).resolve().parent.parent / "data" / "users.json"
ITERATIONS = 310_000

def _load_users() -> dict:
    if not USERS_FILE.exists():
        return {}
    try:
        with USERS_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}

def _save_users(users: dict) -> None:
    USERS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with USERS_FILE.open("w", encoding="utf-8") as file:
        json.dump(users, file, indent=2)

def _password_hash(password: str, salt_hex: str | None = None) -> tuple[str, str]:
    salt = bytes.fromhex(salt_hex) if salt_hex else secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, ITERATIONS)
    return salt.hex(), digest.hex()

def create_account(name: str, email: str, password: str) -> tuple[bool, str]:
    name = name.strip()
    email = email.strip().lower()

    if len(name) < 2:
        return False, "Please enter your full name (at least 2 characters)."
    if "@" not in email or "." not in email.split("@")[-1]:
        return False, "Please enter a valid email address."
    if len(password) < 8:
        return False, "Password must contain at least 8 characters."

    users = _load_users()
    if email in users:
        return False, "An account with this email already exists. Please sign in."

    salt, password_digest = _password_hash(password)
    users[email] = {
        "name": name,
        "salt": salt,
        "password_hash": password_digest,
    }
    _save_users(users)
    return True, "Account created successfully. You can now sign in."

def sign_in(email: str, password: str) -> tuple[bool, str, dict | None]:
    email = email.strip().lower()
    user = _load_users().get(email)

    if not user:
        return False, "Email or password is incorrect.", None

    _, supplied_digest = _password_hash(password, user["salt"])
    if not hmac.compare_digest(supplied_digest, user["password_hash"]):
        return False, "Email or password is incorrect.", None

    return True, "Signed in successfully.", {"email": email, "name": user["name"]}
