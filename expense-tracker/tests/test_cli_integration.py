import subprocess
import sys
import os
import pytest

CLI_CMD = [sys.executable, "-m", "expense_tracker"]


def run_cli(args, input_data=None):
    result = subprocess.run(CLI_CMD + args, input=input_data, capture_output=True, text=True)
    return result


@pytest.mark.usefixtures("init_expense_and_budget_file_empty")
def test_add_and_list():
    result = run_cli(["add", "--description", "Lunch", "--amount", "12.5", "--category", "Food"])
    assert result.returncode == 0
    result = run_cli(["list"])
    assert "Lunch" in result.stdout
    assert "12.5" in result.stdout


@pytest.mark.usefixtures("init_expense_and_budget_file_empty")
def test_update_and_summary():
    result = run_cli(["add", "--description", "Book", "--amount", "30", "--category", "Education"])
    assert result.returncode == 0
    result = run_cli(["update", "--id", "1", "--amount", "15"])
    assert result.returncode == 0
    result = run_cli(["summary"])
    assert "30" not in result.stdout and "15" in result.stdout


@pytest.mark.usefixtures("init_expense_and_budget_file_empty")
def test_delete():
    result = run_cli(["add", "--description", "Snack", "--amount", "5", "--category", "Food"])
    assert result.returncode == 0
    result = run_cli(["delete", "--id", "1"])
    assert result.returncode == 0
    result = run_cli(["list"])
    assert "Snack" not in result.stdout


@pytest.mark.usefixtures("init_expense_and_budget_file_empty")
def test_budget_and_export(tmp_path):
    result = run_cli(["budget", "--month", "1", "--amount", "100"])
    assert result.returncode == 0
    csv_path = tmp_path / "export.csv"
    result = run_cli(["export", "--csv", str(csv_path)])
    assert result.returncode == 0
    assert os.path.exists(csv_path)
