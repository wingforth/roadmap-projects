"""Configuration

DATABASE: The file that saves expenses.
BUDGET: The file that saves budgets.
"""

from pathlib import Path


DATA_DIR = Path(__file__).resolve().parent.parent / "data/"
DATABASE = DATA_DIR / "expenses.csv"
BUDGET = DATA_DIR / "budgets.json"
