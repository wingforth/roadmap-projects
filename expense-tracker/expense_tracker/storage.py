"""Use a CSV file for storage."""

import csv
import json
from datetime import date
from pathlib import Path
from expense_tracker.expense import Expense


def _str2date(date_string: str) -> date:
    """Convert a string in the format "YEAR-MONTH-DAY" to a date.

    Args:
        date_string (str): A string in the format 'YEAR-MONTH-DAY'.

    Returns:
        date: A date represented by date_string.
    """
    return date(*(int(item) for item in date_string.split("-")))


def _ensure_dir_exist(directory: Path) -> None:
    """Ensure a directory exists, otherwise create it."""
    if not directory.exists():
        directory.mkdir(parents=True, exist_ok=True)
    elif not directory.is_dir():
        raise NotADirectoryError(f"{directory} is not a directory.")


def load_expenses(csv_file: Path) -> list[Expense]:
    """Load a list of Expense objects from a CSV file."""
    if not csv_file.exists():
        return []
    with open(csv_file, mode="r", encoding="utf-8", newline="") as fd:
        reader = csv.reader(fd, quoting=csv.QUOTE_NONNUMERIC)
        first_line = next(reader, None)
        if first_line is None:
            return []
        expenses = []
        if tuple(first_line) != Expense.fields():
            try:
                id_, *_, create_at = first_line
                expenses.append(Expense(int(id_), *_, _str2date(create_at)))  # type: ignore
            except csv.Error as e:
                raise SystemExit(f"failed to read CSV file: file {csv_file}, line {reader.line_num}: {e}")
        try:
            expenses.extend(Expense(int(id_), *_, _str2date(create_at)) for id_, *_, create_at in reader)  # type: ignore
        except csv.Error as e:
            raise SystemExit(f"failed to read CSV file: file {csv_file}, line {reader.line_num}: {e}")
    return expenses


def save_expenses(csv_file: Path, expenses: list[Expense], include_header: bool = False) -> None:
    """Save a list of Expense objects to a CSV file."""
    _ensure_dir_exist(csv_file.parent)
    with open(csv_file, mode="w", encoding="utf-8", newline="") as fd:
        writer = csv.writer(fd, quoting=csv.QUOTE_NONNUMERIC)
        if include_header:
            writer.writerow(Expense.fields())
        writer.writerows(exp.to_tuple() for exp in expenses)


def append_expense(csv_file: Path, expense: Expense) -> None:
    """Append an Expense object to a CSV file."""
    _ensure_dir_exist(csv_file.parent)
    with open(csv_file, mode="a", encoding="utf-8", newline="") as fd:
        writer = csv.writer(fd, quoting=csv.QUOTE_NONNUMERIC)
        writer.writerow(expense.to_tuple())


def load_budgets(json_file: Path) -> list[float | None]:
    """Load budgets for months from a JSON file."""
    if not json_file.exists():
        return [None] + [float("inf")] * 12
    with open(json_file, mode="r", encoding="utf-8") as fd:
        try:
            return json.load(fd)
        except json.JSONDecodeError:
            return [None] + [float("inf")] * 12


def save_budgets(json_file: Path, budgets: list[float | None]) -> None:
    """Save budgets for months to a JSON file."""
    _ensure_dir_exist(json_file.parent)
    with open(json_file, mode="w", encoding="utf-8") as fd:
        json.dump(budgets, fd)
