import pytest
from datetime import date
from expense_tracker.config import BUDGET, DATABASE
from expense_tracker.expense import Expense
from expense_tracker.storage import save_budgets, save_expenses


@pytest.fixture
def init_expenses():
    return [
        Expense(1, "Lunch", 15, "Food", date(2024, 7, 1)),
        Expense(2, "Dinner", 28.5, "Food", date(2025, 3, 2)),
        Expense(3, "Book", 45.0, "Education", date(2025, 4, 10)),
        Expense(4, "Bus Ticket", 2.5, "Transport", date(2025, 4, 15)),
        Expense(5, "Movie", 30.0, "Entertainment", date(2025, 5, 5)),
        Expense(6, "Coffee", 8, "Food", date(2025, 5, 6)),
        Expense(7, "Gym", 60.0, "Health", date(2025, 6, 1)),
        Expense(8, "Gift", 100.0, "Other", date(2025, 6, 20)),
        Expense(9, "Taxi", 25.0, "Transport", date(2025, 7, 2)),
        Expense(10, "Notebook", 12.0, "Education", date(2025, 7, 15)),
    ]


@pytest.fixture
def init_budgets():
    return [None, 30.0, 40.0, 50.0, 50.0, float("inf"), 200.0, 50.0, 50.0, 50.0, 50.0, 50.0, 50.0]


@pytest.fixture
def init_expense_and_budget_file_data(init_expenses, init_budgets):
    save_expenses(DATABASE, init_expenses)
    save_budgets(BUDGET, init_budgets)
    yield
    save_expenses(DATABASE, [])
    save_budgets(BUDGET, [None] + [float("inf")] * 12)


@pytest.fixture
def init_expense_and_budget_file_empty():
    DATABASE.unlink(missing_ok=True)
    BUDGET.unlink(missing_ok=True)
    yield
    DATABASE.unlink(missing_ok=True)
    BUDGET.unlink(missing_ok=True)


@pytest.fixture
def tmp_csv_file_for_expenses(tmp_path):
    return tmp_path / "expenses.csv"


@pytest.fixture
def tmp_json_file_for_budgets(tmp_path):
    return tmp_path / "budgets.json"
