import pytest
from datetime import date
from argparse import Namespace
from expense_tracker.cli import CLI, MONTH_NAMES
from expense_tracker.config import DATABASE, BUDGET
from expense_tracker.expense import Expense
from expense_tracker.storage import load_expenses, load_budgets


@pytest.mark.usefixtures("init_expense_and_budget_file_data")
@pytest.mark.parametrize(
    "description,amount,category,exceed",
    [
        # not exceed budget
        ("Breakfast", 20, "Food", False),
        # exceed budget
        ("Pen", 20, "Education", True),
    ],
)
def test_handle_add(init_expenses, description, amount, category, exceed, capsys):
    cli = CLI()
    args = Namespace(
        description=description, amount=amount, category=category, create_at=date(2025, 7, 17), sub_cmd="add"
    )
    cli.handle_add(args)
    loaded = load_expenses(DATABASE)
    new_id = init_expenses[-1].id + 1
    new_exp = Expense(new_id, description, amount, category, date(2025, 7, 17))
    assert loaded == init_expenses + [new_exp]
    if exceed:
        assert "exceed" in capsys.readouterr().out


@pytest.mark.usefixtures("init_expense_and_budget_file_data")
@pytest.mark.parametrize(
    "id_,description,amount,category,exceed,exist",
    [
        # exceed budget
        (1, "Dinner", 55, "Food", True, True),
        # not exceed budget
        (8, "Gift", 125, "Life", False, True),
        # not exist
        (12, "Gift", 125, "Life", False, False),
    ],
)
def test_handle_update(init_expenses, id_, description, amount, category, exceed, exist, capsys):
    cli = CLI()
    args = Namespace(id=id_, description=description, amount=amount, category=category, sub_cmd="update")
    cli.handle_update(args)
    if not exist:
        assert "not exist" in capsys.readouterr().out
        return
    loaded = load_expenses(DATABASE)
    # The index of the id_ expense is id_ - 1
    init_expenses[id_ - 1].update(description=description, amount=amount, category=category)
    assert loaded == init_expenses
    if exceed:
        assert "exceed" in capsys.readouterr().out


@pytest.mark.usefixtures("init_expense_and_budget_file_data")
@pytest.mark.parametrize(
    "id_,exist",
    [
        (1, True),
        (5, True),
        # not exist
        (11, False),
    ],
)
def test_handle_delete(init_expenses, id_, exist, capsys):
    cli = CLI()
    args = Namespace(id=id_, sub_cmd="delete")
    cli.handle_delete(args)
    if not exist:
        assert "not exist" in capsys.readouterr().out
        return
    loaded = load_expenses(DATABASE)
    init_expenses.pop(id_ - 1)
    assert loaded == init_expenses


@pytest.mark.usefixtures("init_expense_and_budget_file_data")
@pytest.mark.parametrize(
    "month,year,category,indices",
    [
        # list all
        (None, None, None, range(10)),
        # list expenses for year 2025
        (None, 2025, None, range(1, 10)),
        # list expenses for May of current year
        (5, None, None, [4, 5]),
        # list expenses for July 2024
        (7, 2024, None, [0]),
        # list expenses for category Food
        (None, None, "Food", [0, 1, 5]),
        # list expenses for category Food in year 2025
        (None, 2025, "Food", [1, 5]),
        # list expenses for category Health in June 2025
        (6, 2025, "Health", [6]),
        # list expenses for category Health in May of current year
        (5, None, "Food", [5]),
        # list expenses for a non-exist category
        (None, None, "NonExist", []),
    ],
)
def test_handle_list(init_expenses, capsys, month, year, category, indices):
    cli = CLI()
    args = Namespace(month=month, year=year, category=category, sub_cmd="list")
    cli.handle_list(args)
    captured = capsys.readouterr()
    lines = captured.out.splitlines()[2:]
    for line, index in zip(lines, indices):
        expense = init_expenses[index]
        assert line.split() == [
            str(expense.id),
            str(expense.create_at),
            *expense.description.split(),
            f"${float(expense.amount)}",
            *expense.category.split(),
        ]


@pytest.mark.usefixtures("init_expense_and_budget_file_data")
@pytest.mark.parametrize(
    "month,year,category,excepted",
    [
        # summary of all
        (None, None, None, "Total expenses: $326.0\n"),
        # summary of a non-exist category
        (None, None, "NonExist", "NonExist expenses: $0\n"),
        # summary of year 2025
        (None, 2025, None, "Total expenses in 2025: $311.0\n"),
        # summary of April of current year
        (4, None, None, "Total expenses in April: $47.5\n"),
        # summary of category Food
        (None, None, "Food", "Food expenses: $51.5\n"),
        # summary of category Food in year 2025
        (None, 2025, "Food", "Food expenses in 2025: $36.5\n"),
        # summary of category Food in May of current year
        (5, None, "Food", "Food expenses in May: $8.0\n"),
        # summary of category Food in July 2024
        (7, 2024, "Food", "Food expenses in July 2024: $15.0\n"),
    ],
)
def test_handle_summary(capsys, month, year, category, excepted):
    cli = CLI()
    args = Namespace(month=month, year=year, category=category, sub_cmd="summary")
    expenses = load_expenses(DATABASE)
    # assert expenses[0] == Expense(1, "Lunch", 15, "Food", date(2024, 7, 1))
    assert len(expenses) == 10
    cli.handle_summary(args)
    captured = capsys.readouterr()
    assert captured.out == excepted


@pytest.mark.usefixtures("init_expense_and_budget_file_data")
@pytest.mark.parametrize("month", [[1], [1, 2], range(1, 13)])
def test_handle_budget_show(init_budgets, month, capsys):
    cli = CLI()
    args = Namespace(month=month, amount=None, sub_cmd="budget")
    cli.handle_budget(args)
    captured = capsys.readouterr()
    lines = captured.out.splitlines()[2:]
    assert len(lines) == len(month)
    for line, m in zip(lines, month):
        assert line.split() == [MONTH_NAMES[m], str(init_budgets[m])]


@pytest.mark.usefixtures("init_expense_and_budget_file_data")
@pytest.mark.parametrize("month", [[1], [1, 2], range(1, 13)])
@pytest.mark.parametrize("amount", [10, 20.5, float("inf")])
def test_handle_budget_set(init_budgets, month, amount):
    cli = CLI()
    args = Namespace(month=month, amount=amount, sub_cmd="budget")
    cli.handle_budget(args)
    loaded = load_budgets(BUDGET)
    for m in month:
        init_budgets[m] = amount
    assert loaded == init_budgets


@pytest.mark.usefixtures("init_expense_and_budget_file_data")
@pytest.mark.parametrize("include", [True, False])
def test_handle_export(init_expenses, tmp_path, include):
    cli = CLI()
    csv_file = tmp_path / "export.csv"
    args = Namespace(csv=csv_file, include=include, sub_cmd="export")
    cli.handle_export(args)
    loaded = load_expenses(csv_file)
    assert loaded == init_expenses
