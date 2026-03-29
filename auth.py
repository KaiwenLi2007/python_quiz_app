"""Registration, login, and password hashing."""

from __future__ import annotations

import hashlib
import secrets


def hash_password(password: str) -> tuple[str, str]:
    """Return (hex digest, salt) using SHA-256 over salt+password."""
    salt = secrets.token_hex(16)
    digest = hashlib.sha256((salt + password).encode("utf-8")).hexdigest()
    return digest, salt


def verify_password(password: str, salt: str, stored_hash: str) -> bool:
    digest = hashlib.sha256((salt + password).encode("utf-8")).hexdigest()
    return secrets.compare_digest(digest, stored_hash)


def register_user(users: dict, username: str, password: str) -> tuple[bool, str]:
    """
    Register a new user. Returns (ok, message).
    On success, mutates users in place (caller must save).
    """
    username = username.strip()
    if not username:
        return False, "Username cannot be empty."
    if username in users:
        return False, "That username is already taken."
    if not password:
        return False, "Password cannot be empty."
    digest, salt = hash_password(password)
    users[username] = {
        "password_hash": digest,
        "salt": salt,
        "total_quizzes": 0,
        "total_points": 0.0,
        "average_score": 0.0,
        "likes": {},
    }
    return True, "Registered successfully."


def authenticate(users: dict, username: str, password: str) -> bool:
    username = username.strip()
    rec = users.get(username)
    if not rec:
        return False
    return verify_password(password, rec["salt"], rec["password_hash"])
