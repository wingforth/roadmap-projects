# Expense Tracker

A simple expense tracker application to manage finances.

## Features

- Add, update, delete, list, and summarize expenses
- Set and view monthly budgets
- Export expenses to CSV
- Command-line interface

## Requirements

- Python 3.8+
- git

## Installation

Clone this repository with git:

   ```sh
   git clone https://github.com/wingforth/roadmap-projects
   cd roadmap-projects/expense-tracker
   ```

## Usage

Run the CLI:

```sh
python -m expense_tracker [COMMAND] [OPTIONS]
```

### Commands

- expense-tracker add --description=DESCRIPTION --amount=AMOUNT --category=CATEGORY
- expense-tracker update --id=ID [--description=DESCRIPTION] [--amount=AMOUNT] [--category=CATEGORY]
- expense-tracker delete --id=ID
- expense-tracker list [--month=MONTH] [--year YEAR] [--category=CATEGORY]
- expense-tracker summary [--month=MONTH] [--year YEAR] [--category=CATEGORY]
- expense-tracker budget [--month MONTH [MONTH ...]] [--amount=AMOUNT]
- expense-tracker export --csv=CSV [--include]

### Options

- `--description`: Description of the expense
- `--amount`: Amount (non-negative float)
- `--category`: Category of the expense
- `--id`: Expense ID
- `--month`: Month (1-12)
- `--year`: Year (e.g. 2024)
- `--csv`: Path to export CSV file
- `--include`: Include header in exported CSV

### Examples

Add an expense:

```sh
python -m expense_tracker add --description "Lunch" --amount 12.5 --category Food
```

List all expenses:

```sh
python -m expense_tracker list
```

Update an expense:

```sh
python -m expense_tracker update --id 1 --amount 15
```

Delete an expense:

```sh
python -m expense_tracker delete --id 1
```

View summary for July 2024:

```sh
python -m expense_tracker summary --month 7 --year 2024
```

Set budget for January:

```sh
python -m expense_tracker budget --month 1 --amount 100
```

Export expenses to CSV:

```sh
python -m expense_tracker export --csv export.csv --include
```

## Data Files

- Expenses are stored in `data/expenses.csv`
- Budgets are stored in `data/budgets.json`
