# from random import randint
import random
import time
from number_guessing_game.config import DIFFICULTY, SCORE_FILE
from number_guessing_game.score import TopScoreList


def _input_int(message: str = "", bound: tuple[int, int] | None = None) -> int:
    while True:
        s = input(message).strip()
        try:
            integer = int(s)
        except ValueError:
            print("Invalid input. Please enter a valid number.")
            continue
        if bound and not bound[0] <= integer <= bound[1]:
            print(f"Invalid input. Please enter a number in the range {list(bound)} (including both end points).")
            continue
        return integer


def set_difficulty_level() -> tuple[str, int]:
    print("\nPlease select the difficulty level:")
    for i, (level, chances) in enumerate(DIFFICULTY, 1):
        print(f"{i}. {level} ({chances} chances)")
    print()
    choice = _input_int("Enter your choice: ", (1, len(DIFFICULTY)))
    difficulty = DIFFICULTY[choice - 1]
    print(f"\nGreat! You have selected the {difficulty[0]} difficulty level. You have {difficulty[1]} chances.")
    return difficulty


def guess(secret: int, chances: int) -> tuple[int, float] | None:
    print("\nLet's start the game!\n")
    start = time.perf_counter()
    for attempts in range(1, chances + 1):
        answer = _input_int("Enter your guess: ")
        if answer == secret:
            elapsed = round(time.perf_counter() - start, 2)
            print(f"Congratulations! You guessed the correct number in {attempts} attempts. It took {elapsed} seconds.")
            return (attempts, elapsed)
        if answer < secret:
            print(f"Incorrect! The number is greater than {answer}")
        else:
            print(f"Incorrect! The number is less than {answer}")
        provide_hint(secret, answer, chances - attempts)
    else:
        print(f"Sorry, you have run out of chances! The secret number is {secret}.")


def provide_hint(secret: int, guess: int, attempts_left: int) -> None:
    if attempts_left == 1:
        for num in (3, 5, 7):
            if secret % num == 0:
                print(f"Hint: The secret number is a multiple of {num}.")
                break
        else:
            print(f"Hint: The sum of digits in the secret number is {sum(map(int, str(secret)))}")
    elif attempts_left == 2:
        print(f"Hint: The secret number is {'even' if secret % 2 == 0 else 'odd'}.")
    elif attempts_left == 3:
        diff = abs(secret - guess)
        if diff <= 5:
            print("Hint: You're very close!")
        elif diff <= 10:
            print("Hint: You're close! Within 10 numbers.")
        else:
            print("Hint: You're very far!")


def rank(top_list: TopScoreList, score: tuple[int, float], difficulty_level: str) -> None:
    ranking = top_list.ranking(score, difficulty_level)
    if ranking is None:
        return
    suffix = ["th", "st", "nd", "rd"][ones if (ones := ranking % 10) < 4 else 0]
    print(f"\nCongratulations! You got {ranking}{suffix} place in the all-time ranking.")
    player = input("Please enter your name to record this ranking: ").strip()
    top_list.update_scores(ranking, score, player, difficulty_level)
    show_top_score_list(top_list, difficulty_level)


def show_top_score_list(top_list: TopScoreList, difficulty_level: str) -> None:
    print(f"Do you want to view the top score list on {difficulty_level} difficulty level (Y/n).")
    while (reply := input().strip().lower()) not in ("y", "n", ""):
        print("Please enter `y` or `n`.")
    if reply == "n":
        return
    fmt = "{:^7} {:^8} {:^10} {}".format
    print(fmt("ranking", "attempts", "elapsed(s)", "player"))
    for ranking, (attempts, elapsed, player) in enumerate(top_list.get_top_score_list(difficulty_level), 1):
        print(fmt(ranking, attempts, elapsed, player))


def play_game() -> None:
    print(
        "Welcome to the Number Guessing Game!\n"
        "I'm thinking of a number between 1 and 100.\n"
        "You have several chances to guess the correct number."
    )
    with TopScoreList(10, SCORE_FILE) as top_list:
        level, chances = set_difficulty_level()
        while True:
            secret_number = random.randint(1, 100)
            if (score := guess(secret_number, chances)) is not None:
                rank(top_list, score, level)
            print("\nDo you want to play again?\n1. Play again.\n2. Select a new difficulty level and play.\n3. Quite.")
            reply = _input_int("Your reply: ", bound=(1, 3))
            if reply == 3:
                break
            if reply == 2:
                level, chances = set_difficulty_level()
