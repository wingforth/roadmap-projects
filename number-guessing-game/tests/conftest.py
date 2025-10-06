import pytest
import json
from number_guessing_game.config import DIFFICULTY, SCORE_FILE

scores = {
    "Easy": [(1, 5.23, "Bob"), (4, 18.234, "Jack")],
    "Medium": [],
    "Hard": [],
}
empty_scores = {level: [] for level, _ in DIFFICULTY}


@pytest.fixture
def init_top_score_list():
    with open(SCORE_FILE, mode="w", encoding="utf-8") as fd:
        json.dump(scores, fd, indent=4)
    yield
    with open(SCORE_FILE, mode="w", encoding="utf-8") as fd:
        json.dump(empty_scores, fd, indent=4)


@pytest.fixture
def clear_top_list():
    with open(SCORE_FILE, mode="w", encoding="utf-8") as fd:
        json.dump(empty_scores, fd, indent=4)
    yield
    with open(SCORE_FILE, mode="w", encoding="utf-8") as fd:
        json.dump(empty_scores, fd, indent=4)
