"""CLI entry: menus, quiz flow, and wiring auth, storage, and quiz_engine."""

from __future__ import annotations

import sys

import auth
import quiz_engine as qe
import storage


def prompt_choice(prompt: str, valid: set[str]) -> str:
    while True:
        s = input(prompt).strip()
        if s in valid:
            return s
        print("Invalid input")


def prompt_int(prompt: str, minimum: int = 1, maximum: int | None = None) -> int:
    while True:
        raw = input(prompt).strip()
        try:
            n = int(raw)
        except ValueError:
            print("Invalid input")
            continue
        if n < minimum:
            print("Invalid input")
            continue
        if maximum is not None and n > maximum:
            print("Invalid input")
            continue
        return n


def prompt_yes_no(prompt: str) -> bool:
    while True:
        s = input(prompt).strip().lower()
        if s in ("y", "yes"):
            return True
        if s in ("n", "no"):
            return False
        print("Invalid input")


def login_or_register(users: dict) -> str:
    while True:
        print('Wanna (1) Log in or (2) Register?')
        choice = prompt_choice("> ", {"1", "2"})
        if choice == "2":
            user = input("Choose a username: ").strip()
            pw = input("Choose a password: ")
            ok, msg = auth.register_user(users, user, pw)
            print(msg)
            if ok:
                storage.save_users(users)
                return user
            continue
        user = input("Username: ").strip()
        pw = input("Password: ")
        if auth.authenticate(users, user, pw):
            return user
        print("Invalid username or password.")


def show_main_menu(username: str) -> str:
    print(f"\nHi, {username}!")
    print("[1] Take a Quiz")
    print("[2] View Stats")
    print("[3] Exit")
    return prompt_choice("> ", {"1", "2", "3"})


def show_stats(user: dict) -> None:
    print("\n--- Your stats ---")
    print(f"Total quizzes: {user['total_quizzes']}")
    print(f"Total points (all quizzes): {user['total_points']:.1f}")
    print(f"Average score per quiz: {user['average_score']:.2f}")
    likes = sum(1 for v in user.get("likes", {}).values() if v is True)
    dislikes = sum(1 for v in user.get("likes", {}).values() if v is False)
    print(f"Questions liked: {likes}, disliked: {dislikes}")


def run_quiz(username: str, users: dict, questions: list[dict]) -> None:
    user = users[username]
    likes = user.get("likes", {})
    # Normalize keys to int (pickle may have str keys from older runs)
    likes_int = {int(k): v for k, v in likes.items()}

    n = prompt_int(
        f"How many questions? (1–{len(questions)}): ",
        minimum=1,
        maximum=len(questions),
    )
    pairs = qe.smart_shuffle_select(questions, likes_int, n)
    score = 0.0
    possible = float(len(pairs))

    for qid, q in pairs:
        print()
        print(f"Category: {q.get('category', 'General')}")
        print(f"Type: {qe.type_label(q['type'])}")
        print(q["question"])
        if q["type"] == "multiple_choice":
            for i, opt in enumerate(q.get("options") or [], start=1):
                print(f"  {i}) {opt}")

        used_hint = False
        if prompt_yes_no("Want a hint for 0.5 points? (y/n): "):
            used_hint = True
            print(f"Hint: {q.get('hint', '(no hint available)')}")

        while True:
            ans = input("Your answer: ")
            status, pts, correct = qe.grade_answer(q, ans, used_hint)
            if status == "invalid":
                print("Invalid input")
                continue
            score += pts
            if correct:
                print("Correct!")
            else:
                ca = qe.format_correct_answer(q)
                print(f"Wrong. The correct answer is: {ca}")
            break

        liked = prompt_yes_no("Did you like this question? (y/n): ")
        likes_int[qid] = liked
        user["likes"] = {str(k): v for k, v in likes_int.items()}
        storage.save_users(users)

    print(f"\nFinal score: {score:.1f}/{possible:.1f}!")

    tq = user["total_quizzes"] + 1
    user["total_quizzes"] = tq
    user["total_points"] = user["total_points"] + score
    user["average_score"] = (user["average_score"] * (tq - 1) + score) / tq
    storage.save_users(users)


def main() -> None:
    try:
        questions = storage.load_questions()
    except FileNotFoundError:
        print("Oops! Can't find questions.json")
        sys.exit(1)

    users = storage.load_users()
    username = login_or_register(users)

    while True:
        choice = show_main_menu(username)
        if choice == "3":
            print("Goodbye!")
            break
        if choice == "2":
            show_stats(users[username])
            continue
        run_quiz(username, users, questions)


if __name__ == "__main__":
    main()
