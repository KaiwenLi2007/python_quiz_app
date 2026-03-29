"""Load questions from JSON and persist user data with pickle."""

from __future__ import annotations

import json
import pickle
from pathlib import Path

_BASE = Path(__file__).resolve().parent
QUESTIONS_PATH = _BASE / "questions.json"
USERS_PATH = _BASE / "users.dat"


def load_questions() -> list[dict]:
    """Load questions from questions.json. Caller handles FileNotFoundError."""
    with open(QUESTIONS_PATH, encoding="utf-8") as f:
        data = json.load(f)
    return data["questions"]


def load_users() -> dict:
    """
    Load users from users.dat. If the file is missing or corrupt, return {}.
    """
    if not USERS_PATH.exists():
        return {}
    try:
        with open(USERS_PATH, "rb") as f:
            return pickle.load(f)
    except Exception as e:
        print(
            f"Warning: users.dat could not be read ({e!s}). Starting with a fresh user database."
        )
        try:
            USERS_PATH.unlink()
        except OSError:
            pass
        return {}


def save_users(users: dict) -> None:
    """Write users dict to users.dat."""
    with open(USERS_PATH, "wb") as f:
        pickle.dump(users, f)
