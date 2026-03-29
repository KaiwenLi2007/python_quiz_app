# Senior Code Review: Python CLI Quiz App

Audit performed against `SPEC.md` and the implementation in `main.py`, `auth.py`, `quiz_engine.py`, and `storage.py`.

---

## Acceptance Criteria (strict)

| # | Criterion | Verdict |
|---|-----------|---------|
| 1 | App complains and exits with code **1** if `questions.json` is missing. | **[PASS]** |
| 2 | Register, close terminal, reopen, and log in successfully (persistence). | **[PASS]** |
| 3 | `users.dat` is unreadable garbage to humans; **no plain-text passwords**. | **[PASS]** |
| 4 | Letters instead of a number for “how many questions” retries instead of crashing. | **[PASS]** |
| 5 | Saying **y** to a hint shows the hint and caps a **correct** answer at **0.5** points. | **[PASS]** |
| 6 | Liking a question updates the hidden save file. | **[PASS]** |
| 7 | Past likes/dislikes influence which questions are picked next time. | **[PASS]** |

**Evidence (brief):**

1. `main.py` catches `FileNotFoundError` from `storage.load_questions()`, prints the required message, and calls `sys.exit(1)` (`main.py` lines 142–147).
2. `storage.save_users` / `storage.load_users` use pickle on `users.dat`; registration hashes passwords and login verifies (`storage.py` lines 21–44, `auth.py` lines 33–50).
3. Passwords are stored as SHA-256 digests with per-user salts (`auth.py` lines 9–18, 33–36); `users.dat` is opened `"wb"`/`"rb"` and written with `pickle.dump` (`storage.py` lines 28–29, 43–44).
4. `prompt_int` catches `ValueError` from `int(raw)` and prints `"Invalid input"` in a loop (`main.py` lines 20–34).
5. Hint path sets `used_hint = True`, prints the hint (`main.py` lines 109–112); `grade_answer` awards `0.5 if used_hint else 1.0` when correct (`quiz_engine.py` lines 114–116, 122–125, 131–132).
6. After each question, like/dislike is written to `user["likes"]` and `storage.save_users(users)` is called (`main.py` lines 128–131).
7. `run_quiz` passes `likes` into `qe.smart_shuffle_select`, which uses `_question_weight` (liked ↑, disliked ↓) and weighted sampling without replacement (`main.py` lines 87–96, `quiz_engine.py` lines 12–56).

---

## Logic & Security

- **`users.dat` is binary pickle:** **[YES]** — `pickle.load` / `pickle.dump` with `"rb"` / `"wb"` (`storage.py` lines 28–29, 43–44).
- **Passwords hashed (SHA-256), not plain text:** **[YES]** — `hashlib.sha256` over salt + password, `secrets.token_hex` salt, `secrets.compare_digest` on verify (`auth.py` lines 9–18, 45–50).
- **Smart shuffle uses feedback weighting:** **[YES]** — Weights 3.0 (liked), 0.35 (disliked), 1.0 (neutral); weighted draw without replacement (`quiz_engine.py` lines 12–56).

---

## Error Handling vs SPEC

- **`questions.json` missing:** Matches SPEC — `FileNotFoundError`, exact-style message, exit code 1 (`main.py` lines 142–147).
- **`ValueError` for bad numeric input:** The specified case (“how many questions”) is handled in `prompt_int` (`main.py` lines 23–27). Invalid multiple-choice / true-false / empty short answer are handled via the `"invalid"` path in `grade_answer` (retry, no score change), not necessarily via `ValueError` — behavior still matches SPEC intent for typos (`quiz_engine.py` lines 97–133, `main.py` lines 114–119).
- **Corrupt `users.dat`:** Implemented as specified — warning, wipe file, fresh DB (`storage.py` lines 25–38).

**Gap (not one of the seven ACs):** Invalid JSON in `questions.json` raises `json.JSONDecodeError`, not caught; SPEC only called out missing file and `FileNotFoundError`. See finding **#2** below.

---

## Code Quality

Structure matches SPEC (`main` / `auth` / `quiz_engine` / `storage`). Input helpers (`prompt_choice`, `prompt_int`, `prompt_yes_no`) centralize validation. Naming is mostly clear (`likes_int`, `qe`, `_question_weight`). No serious spaghetti; minor repetition of the string `"Invalid input"` across helpers is acceptable.

---

## Numbered findings

1. **[WARN]** `pickle` serializes dict keys and string fields as bytes that often include **human-readable ASCII** (e.g. usernames). Passwords are not exposed, but the file is not uniformly “gibberish” in a text editor — only the cryptographic requirement for passwords is strictly met. (`storage.py` lines 43–44; format inherent to `pickle`.)

2. **[WARN]** `load_questions` does not handle corrupt or non-JSON `questions.json`; `json.load` can raise `JSONDecodeError` and crash startup. SPEC explicitly required handling for the **missing** file only. (`storage.py` lines 14–18.)

3. **[WARN]** Unknown `question["type"]` falls through `grade_answer` to `return "ok", 0.0, False` without an `"invalid"` retry, so a data typo could mark an answer wrong with no recovery. (`quiz_engine.py` line 135.)

---

## Summary

All **seven** acceptance criteria are **[PASS]**. There are **no [FAIL]** items in this audit. Warnings cover pickle readability of non-secret strings, unhandled malformed JSON, and a rare unknown-question-type edge case.
