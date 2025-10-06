import json
from collections import deque
from pathlib import Path
from number_guessing_game.config import DIFFICULTY


class TopScoreList:
    """Manages top scores for each difficulty level."""

    def __init__(self, max_count: int, score_file: Path) -> None:
        self._ensure_dir_exist(score_file.parent)
        # Max number of high scores that are stored for every difficulty level.
        self.max_count: int = max_count
        # File that stores scores.
        self.score_file: Path = score_file
        self.__scores: dict[str, deque[tuple[int, float, str]]] = {}
        self.__updated: bool = False

    @staticmethod
    def _ensure_dir_exist(directory: Path) -> None:
        if not directory.exists():
            directory.mkdir(parents=True, exist_ok=True)
        elif not directory.is_dir():
            raise NotADirectoryError(f"Path {directory} exits, but not a directory.")

    def load_scores(self) -> None:
        if self.score_file.is_dir():
            raise IsADirectoryError(f"Path {self.score_file} exits, but not a file.")
        try:
            with open(self.score_file, mode="r", encoding="utf-8") as fd:
                data = json.load(fd)
        except (json.JSONDecodeError, FileNotFoundError):
            self.__scores = {level: deque(maxlen=self.max_count) for level, _ in DIFFICULTY}
            return
        self.__scores = {level: deque(map(tuple, records), maxlen=self.max_count) for level, records in data.items()}

    def save_scores(self) -> None:
        data = {level: list(records) for level, records in self.__scores.items()}
        with open(self.score_file, mode="w", encoding="utf-8") as fd:
            return json.dump(data, fd, indent=4)
        self.__updated = False

    def ranking(self, score: tuple[int, float], difficulty_level: str) -> int | None:
        high_scores = self.__scores[difficulty_level]
        if len(high_scores) == self.max_count and score >= high_scores[-1][:2]:
            return None
        for ranking, (attempts, elapsed, _) in enumerate(high_scores, 1):
            if score < (attempts, elapsed):
                return ranking
        else:
            return len(high_scores) + 1

    def get_top_score_list(self, difficulty_level: str) -> list[tuple[int, float, str]]:
        return list(self.__scores[difficulty_level])

    def clear(self) -> None:
        for scores in self.__scores.values():
            scores.clear()
        self.save_scores()

    def update_scores(self, ranking: int, score: tuple[int, float], player: str, difficulty_level: str):
        self.__scores[difficulty_level].insert(ranking - 1, (*score, player))
        self.__updated = True

    def __enter__(self):
        self.load_scores()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.__updated:
            self.save_scores()
