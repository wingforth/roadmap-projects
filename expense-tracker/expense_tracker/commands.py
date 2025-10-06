"""Command specification.

Usage:
    expense-tracker add --description=DESCRIPTION --amount=AMOUNT --category=CATEGORY
    expense-tracker update --id=ID --description=DESCRIPTION [--amount=AMOUNT] [--category=CATEGORY]
    expense-tracker update --id=ID --amount=AMOUNT [--category=CATEGORY]
    expense-tracker update --id=ID --category=CATEGORY
    expense-tracker delete --id=ID
    expense-tracker list [--month=MONTH] [--year YEAR] [--category=CATEGORY]
    expense-tracker summary [--month=MONTH] [--year YEAR] [--category=CATEGORY]
    expense-tracker budget [--month MONTH [MONTH ...]] [--amount=AMOUNT]
    expense-tracker export --csv=CSV [--include]
"""

from pathlib import Path
from argparse import ArgumentTypeError


def _non_negative_float(s: str) -> float:
    """Convert a string `s` to a non-negative float.
    Raise `ArgumentTypeError` if cant't.
    """
    try:
        assert (num := float(s)) >= 0
    except (ValueError, AssertionError):
        raise ArgumentTypeError(f"invalid non-negative float: '{s}'")
    return num


COMMANDS = [
    {
        "cmd": "add",
        "args": [
            {
                "name_or_flags": ["--description"],
                "required": True,
                "help": "Matters that incur the expense.",
            },
            {
                "name_or_flags": ["--category"],
                "required": True,
                "help": "The category of expense.",
            },
            {
                "name_or_flags": ["--amount"],
                "type": _non_negative_float,
                "required": True,
                "help": "The amount of the expense",
            },
        ],
        "description": "Add an expense with a description and amount.",
    },
    {
        "cmd": "update",
        "args": [
            {
                "name_or_flags": ["--id"],
                "type": int,
                "required": True,
                "help": "The ID of the expense which will be updated.",
            },
            {
                "name_or_flags": ["--description"],
                "help": "Matters that incur the expense.",
            },
            {
                "name_or_flags": ["--category"],
                "help": "The category of expense.",
            },
            {
                "name_or_flags": ["--amount"],
                "type": _non_negative_float,
                "help": "The amount of the expense.",
            },
        ],
        "description": "Update an expense.",
    },
    {
        "cmd": "delete",
        "args": [
            {
                "name_or_flags": ["--id"],
                "type": int,
                "required": True,
                "help": "The id of expense item.",
            },
        ],
        "description": "Delete an expense item by ID.",
    },
    {
        "cmd": "list",
        "args": [
            {
                "name_or_flags": ["--category"],
                "help": "The category of expense.",
            },
            {
                "name_or_flags": ["--month"],
                "type": int,
                "choices": range(1, 13),
                "metavar": "MONTH",
                "help": "The month of the expense summary. If the year isn't provided, it's of current year.",
            },
            {
                "name_or_flags": ["--year"],
                "type": int,
                "help": "The year of the expense summary.",
            },
        ],
        "description": "List all expenses, or for a specific month or category.",
    },
    {
        "cmd": "summary",
        "args": [
            {
                "name_or_flags": ["--category"],
                "help": "The category of expense.",
            },
            {
                "name_or_flags": ["--month"],
                "type": int,
                "choices": range(1, 13),
                "metavar": "MONTH",
                "help": "The month of the expense summary. If the year isn't provided, it's of current year.",
            },
            {
                "name_or_flags": ["--year"],
                "type": int,
                "help": "The year of the expense summary.",
            },
        ],
        "description": "View a summary of all expenses, or expenses for a specific month or category.",
    },
    {
        "cmd": "budget",
        "args": [
            {
                "name_or_flags": ["--month"],
                "default": range(1, 13),
                "type": int,
                "choices": range(1, 13),
                "nargs": "+",
                "metavar": "MONTH",
                "help": "The month of the budget.",
            },
            {
                "name_or_flags": ["--amount"],
                "type": _non_negative_float,
                "help": "Amount of the budget for a month. INF stands for infinity.",
            },
        ],
        "description": "View or set budgets for months.",
    },
    {
        "cmd": "export",
        "args": [
            {
                "name_or_flags": ["--csv"],
                "type": Path,
                "required": True,
                "help": "The CSV file that expenses are exported to.",
            },
            {
                "name_or_flags": ["--include"],
                "action": "store_true",
                "help": "Whether to include the header in the CSV file.",
            },
        ],
        "description": "Export expenses to a CSV file.",
    },
]
