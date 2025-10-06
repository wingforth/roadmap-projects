import pytest
from number_guessing_game.game import (
    _input_int,
    set_difficulty_level,
    guess,
    play_game,
    provide_hint,
    DIFFICULTY,
)
# test_number_guessing_game.py


@pytest.mark.parametrize(
    "inputs,expected",
    [
        (["5"], 5),
        (["-1", "2"], 2),  # out of bound then valid
        (["abc", "3"], 3),  # invalid then valid
        (["1"], 1),
        (["10"], 10),
    ],
)
def test_input_int(monkeypatch, inputs, expected):
    monkeypatch.setattr("builtins.input", lambda _: inputs.pop(0))
    result = _input_int("msg: ", (1, 10))
    assert result == expected


def test_input_int_no_bound(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "123")
    assert _input_int("msg: ") == 123


@pytest.mark.parametrize(
    "choice",
    [
        "1",  # Easy
        "2",  # Medium
        "3",  # Hard
    ],
)
def test_set_difficulty_level(monkeypatch, capsys, choice):
    difficulty = DIFFICULTY[int(choice) - 1]
    monkeypatch.setattr("builtins.input", lambda _: choice)
    level = set_difficulty_level()
    assert level == difficulty
    out = capsys.readouterr().out
    assert difficulty[0] in out and str(difficulty[1]) in out


def test_guess_correct_first_try(monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", lambda _: "42")
    guess(42, 5)
    out = capsys.readouterr().out
    assert "Congratulations" in out
    assert "1 attempts" in out
    assert out.count("less") == 0
    assert out.count("greater") == 0


def test_guess_correct_last_try(monkeypatch, capsys):
    answers = ["75", "60", "65"]
    monkeypatch.setattr("builtins.input", lambda _: answers.pop(0))
    guess(65, 3)
    out = capsys.readouterr().out
    assert "Congratulations" in out
    assert "3 attempts" in out
    assert out.count("less") == 1
    assert out.count("greater") == 1


@pytest.mark.parametrize(
    "answers,secret,attempts,less,greater",
    [
        (["10", "20"], 20, 2, 0, 1),  # less then correct
        (["70", "50"], 50, 2, 1, 0),  # greater then correct
        (["70", "50", "60"], 60, 3, 1, 1),  # greater, less then correct
    ],
)
def test_guess_incorrect_then_correct(monkeypatch, capsys, answers, secret, attempts, less, greater):
    monkeypatch.setattr("builtins.input", lambda _: answers.pop(0))
    guess(secret, 3)
    out = capsys.readouterr().out
    assert "Incorrect" in out
    assert "Congratulations" in out
    assert f"{attempts} attempts" in out
    assert out.count("less") == less
    assert out.count("greater") == greater


@pytest.mark.parametrize(
    "answers,secret,less,greater",
    [
        (["1", "2", "3"], 5, 0, 3),  # all incorrect (less)
        (["100", "99", "98"], 97, 3, 0),  # all incorrect (greater)
        (["80", "55", "70"], 66, 2, 1),  # all incorrect (greater and less)
    ],
)
def test_guess_all_incorrect(monkeypatch, capsys, answers, secret, less, greater):
    monkeypatch.setattr("builtins.input", lambda _: answers.pop(0))
    guess(secret, 3)
    out = capsys.readouterr().out
    assert "Sorry, you have run out of chances" in out
    assert out.count("less") == less
    assert out.count("greater") == greater


@pytest.mark.usefixtures("clear_top_list")
@pytest.mark.parametrize(
    "inputs,secret,rounds",
    [
        # Simulate: select Medium (2) difficulty, then guess 50, then guess 77 (correct), then quite.
        (["2", "50", "77", "Lee", "n", "3"], [77], 1),
        # Simulate: select medium (2), then guess 50, then guess 77 (correct),
        # then play select Hard (3) difficulty and play again,
        # then guess 90, then guess 85 (correct), then quite.
        (["2", "50", "77", "Lee", "", "2", "3", "90", "85", "Steven", "y", "3"], [77, 85], 2),
        # Simulate: select medium (2), then guess 50, then guess 77 (correct),
        # then play again, then guess 90, then guess 85 (correct), then quite.
        (["2", "50", "77", "Lee", "N", "1", "90", "85", "Steven", "Y", "3"], [77, 85], 2),
    ],
)
def test_play_game_empty_top_list(monkeypatch, capsys, inputs, secret, rounds):
    monkeypatch.setattr("builtins.input", lambda *_: inputs.pop(0))
    monkeypatch.setattr("random.randint", lambda *_: secret.pop(0))
    play_game()
    out = capsys.readouterr().out
    assert "Welcome to the Number Guessing Game" in out
    assert out.count("Do you want to play again?") == rounds


@pytest.mark.usefixtures("init_top_score_list")
@pytest.mark.parametrize(
    "inputs,secret,rounds",
    [
        # Simulate: select Medium (2) difficulty, then guess 50, then guess 77 (correct), then quite.
        (["2", "50", "77", "Lee", "n", "3"], [77], 1),
        # Simulate: select medium (2), then guess 50, then guess 77 (correct),
        # then play select Hard (3) difficulty and play again,
        # then guess 90, then guess 85 (correct), then quite.
        (["2", "50", "77", "Lee", "", "2", "3", "90", "85", "Steven", "y", "3"], [77, 85], 2),
        # Simulate: select medium (2), then guess 50, then guess 77 (correct),
        # then play again, then guess 90, then guess 85 (correct), then quite.
        (["2", "50", "77", "Lee", "N", "1", "90", "85", "Steven", "Y", "3"], [77, 85], 2),
    ],
)
def test_play_game(monkeypatch, capsys, inputs, secret, rounds):
    monkeypatch.setattr("builtins.input", lambda *_: inputs.pop(0))
    monkeypatch.setattr("random.randint", lambda *_: secret.pop(0))
    play_game()
    out = capsys.readouterr().out
    assert "Welcome to the Number Guessing Game" in out
    assert out.count("Do you want to play again?") == rounds


@pytest.mark.parametrize(
    "secret,guess,attempts_left,num",
    [
        (9, 5, 1, 3),
        (35, 21, 1, 5),
        (49, 45, 1, 7),
    ],
)
def test_provide_hint_multiple_of_num(capsys, secret, guess, attempts_left, num):
    provide_hint(secret, guess, attempts_left)
    captured = capsys.readouterr()
    assert f"Hint: The secret number is a multiple of {num}." in captured.out
    assert "Hint: The sum of digits in the secret number is" not in captured.out


@pytest.mark.parametrize(
    "secret,guess,attempts_left,total",
    [
        (17, 5, 1, 8),
        (23, 21, 1, 5),
        (74, 45, 1, 11),
    ],
)
def test_provide_hint_sum_of_digits(capsys, secret, guess, attempts_left, total):
    provide_hint(secret, guess, attempts_left)
    captured = capsys.readouterr()
    assert f"Hint: The sum of digits in the secret number is {total}" in captured.out
    assert "Hint: The secret number is a multiple of" not in captured.out


@pytest.mark.parametrize(
    "secret,guess,attempts_left,odd_or_even",
    [
        (17, 5, 2, "odd"),
        (70, 45, 2, "even"),
    ],
)
def test_provide_hint_even_odd(capsys, secret, guess, attempts_left, odd_or_even):
    provide_hint(secret, guess, attempts_left)
    captured = capsys.readouterr()
    assert f"Hint: The secret number is {odd_or_even}" in captured.out


def test_provide_hint_very_close(capsys):
    provide_hint(10, 8, 3)
    captured = capsys.readouterr()
    assert "Hint: You're very close!" in captured.out


def test_provide_hint_close(capsys):
    provide_hint(20, 12, 3)
    captured = capsys.readouterr()
    assert "Hint: You're close! Within 10 numbers." in captured.out


def test_provide_hint_very_far(capsys):
    provide_hint(30, 10, 3)
    captured = capsys.readouterr()
    assert "Hint: You're very far!" in captured.out
