"""Configurations"""

from pathlib import Path

# Path of the score file
SCORE_FILE = Path(__file__).resolve().parent.parent / "data/scores.json"
# Difficulty levels
DIFFICULTY = [("Easy", 10), ("Medium", 5), ("Hard", 3)]
