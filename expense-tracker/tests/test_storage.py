import pytest
import json
from datetime import date
from expense_tracker.expense import Expense
from expense_tracker.storage import (
    load_expenses,
    save_expenses,
    append_expense,
    load_budgets,
    save_budgets,
    _str2date,
    _ensure_dir_exist,
)


def test_str2date():
    assert _str2date("2025-07-02") == date(2025, 7, 2)


def test_save_and_load_expenses(tmp_csv_file_for_expenses):
    expenses = [
        Expense(1, "Lunch", 10.0, "Food", date(2025, 7, 1)),
        Expense(2, "Book", 20.0, "Education", date(2025, 7, 2)),
    ]
    save_expenses(tmp_csv_file_for_expenses, expenses, include_header=True)
    loaded = load_expenses(tmp_csv_file_for_expenses)
    assert loaded == expenses


def test_save_expenses_empty(tmp_csv_file_for_expenses):
    save_expenses(tmp_csv_file_for_expenses, [], include_header=False)
    loaded = load_expenses(tmp_csv_file_for_expenses)
    assert loaded == []


def test_append_expense(tmp_csv_file_for_expenses):
    expense = Expense(1, "Lunch", 10.0, "Food", date(2025, 7, 1))
    save_expenses(tmp_csv_file_for_expenses, [], include_header=True)
    append_expense(tmp_csv_file_for_expenses, expense)
    loaded = load_expenses(tmp_csv_file_for_expenses)
    assert loaded == [expense]


def test_load_expenses_empty(tmp_path):
    csv_file = tmp_path / "empty.csv"
    assert load_expenses(csv_file) == []


def test_save_and_load_budgets(tmp_json_file_for_budgets):
    budgets = [None] + [100.0] * 12
    save_budgets(tmp_json_file_for_budgets, budgets)
    loaded = load_budgets(tmp_json_file_for_budgets)
    assert loaded == budgets


def test_load_budgets_default(tmp_path):
    json_file = tmp_path / "not_exist.json"
    budgets = load_budgets(json_file)
    assert budgets == [None] + [float("inf")] * 12


def test_load_budgets_empty_file(tmp_json_file_for_budgets):
    tmp_json_file_for_budgets.write_text("")
    budgets = load_budgets(tmp_json_file_for_budgets)
    assert budgets == [None] + [float("inf")] * 12


def test_load_budgets_invalid_file(tmp_json_file_for_budgets):
    tmp_json_file_for_budgets.write_text("not a json")
    budgets = load_budgets(tmp_json_file_for_budgets)
    assert budgets == [None] + [float("inf")] * 12


def test_ensure_dir_exist(tmp_path):
    _ensure_dir_exist(tmp_path)
    file_path = tmp_path / "file.txt"
    file_path.write_text("test")
    with pytest.raises(NotADirectoryError):
        _ensure_dir_exist(file_path)


def test_save_budgets_creates_dir(tmp_path):
    json_file = tmp_path / "subdir" / "budgets.json"
    budgets = [None] + [200.0] * 12
    save_budgets(json_file, budgets)
    assert json.loads(json_file.read_text()) == budgets
