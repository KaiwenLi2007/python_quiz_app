"""Question selection (smart shuffle), grading, and hint scoring."""

from __future__ import annotations

import random


def _normalize(s: str) -> str:
    return " ".join(s.strip().lower().split())


def _question_weight(question_id: int, likes: dict[int, bool]) -> float:
    """
    Liked questions get higher weight; disliked lower; neutral default 1.0.
    """
    if question_id not in likes:
        return 1.0
    if likes[question_id] is True:
        return 3.0
    return 0.35


def smart_shuffle_select(
    questions: list[dict],
    likes: dict[int, bool],
    n: int,
) -> list[tuple[int, dict]]:
    """
    Return up to n (index, question) pairs using weighted sampling without replacement.
    """
    n = min(n, len(questions))
    if n <= 0:
        return []

    pool: list[tuple[int, dict, float]] = [
        (i, q, _question_weight(i, likes)) for i, q in enumerate(questions)
    ]
    chosen: list[tuple[int, dict]] = []
    for _ in range(n):
        if not pool:
            break
        total_w = sum(w for _, _, w in pool)
        if total_w <= 0:
            pick = random.choice(pool)
            pool.remove(pick)
            chosen.append((pick[0], pick[1]))
            continue
        r = random.uniform(0, total_w)
        acc = 0.0
        for idx, item in enumerate(pool):
            acc += item[2]
            if acc >= r:
                chosen.append((item[0], item[1]))
                pool.pop(idx)
                break
    return chosen


def type_label(qtype: str) -> str:
    mapping = {
        "multiple_choice": "Multiple Choice",
        "true_false": "True/False",
        "short_answer": "Short Answer",
    }
    return mapping.get(qtype, qtype)


def parse_multiple_choice_selection(question: dict, raw: str) -> str | None:
    """Return canonical selected option text, or None if invalid."""
    options = question.get("options") or []
    s = raw.strip()
    if not s:
        return None
    if s.isdigit():
        num = int(s)
        if 1 <= num <= len(options):
            return options[num - 1]
        return None
    for o in options:
        if _normalize(o) == _normalize(s):
            return o
    if _normalize(s) == _normalize(str(question["answer"])):
        return str(question["answer"])
    return None


def parse_true_false(raw: str) -> str | None:
    """Return 'true' or 'false', or None if invalid."""
    u = _normalize(raw)
    if u in ("t", "true", "1", "yes", "y"):
        return "true"
    if u in ("f", "false", "0", "no", "n"):
        return "false"
    return None


def grade_answer(
    question: dict,
    raw_answer: str,
    used_hint: bool,
) -> tuple[str, float, bool]:
    """
    Returns (status, points, is_correct).
    status is 'invalid' (retry; no score change) or 'ok'.
    """
    qtype = question["type"]
    correct = question["answer"]

    if qtype == "multiple_choice":
        selected = parse_multiple_choice_selection(question, raw_answer)
        if selected is None:
            return "invalid", 0.0, False
        ok = _normalize(selected) == _normalize(str(correct))
        if not ok:
            return "ok", 0.0, False
        return "ok", (0.5 if used_hint else 1.0), True

    if qtype == "true_false":
        u_norm = parse_true_false(raw_answer)
        if u_norm is None:
            return "invalid", 0.0, False
        c = _normalize(str(correct))
        if u_norm != c:
            return "ok", 0.0, False
        return "ok", (0.5 if used_hint else 1.0), True

    if qtype == "short_answer":
        user = raw_answer.strip()
        if not user:
            return "invalid", 0.0, False
        if _normalize(user) == _normalize(str(correct)):
            return "ok", (0.5 if used_hint else 1.0), True
        return "ok", 0.0, False

    return "invalid", 0.0, False


def format_correct_answer(question: dict) -> str:
    qtype = question["type"]
    ans = question["answer"]
    if qtype == "multiple_choice" and "options" in question:
        opts = question["options"]
        for i, o in enumerate(opts):
            if _normalize(str(o)) == _normalize(str(ans)):
                return f"{i + 1}) {o}"
    return str(ans)
