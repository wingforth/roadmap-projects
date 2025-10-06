from argparse import ArgumentParser, Namespace
from expense_tracker.config import DATABASE, BUDGET
from expense_tracker.commands import COMMANDS
from expense_tracker.expense import Expense, find_by_id, filter_by_date, filter_by_category
from expense_tracker.storage import load_expenses, save_expenses, append_expense, load_budgets, save_budgets


MONTH_NAMES = (
    None,
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
)


class CLI:
    def __init__(self) -> None:
        self.parser = ArgumentParser(
            prog="expense-tracker",
            description="A simple expense tracker application to manage finances.",
        )
        subparser = self.parser.add_subparsers(dest="sub_cmd")
        for command in COMMANDS:
            sub_cmd = subparser.add_parser(command["cmd"], description=command["description"])
            for arg in command["args"]:
                sub_cmd.add_argument(
                    *arg["name_or_flags"], **{key: val for key, val in arg.items() if key != "name_or_flags"}
                )

    def run(self) -> None:
        args = self.parser.parse_args()
        if sub_cmd := getattr(args, "sub_cmd"):
            getattr(self, "handle_" + sub_cmd)(args)
        else:
            self.parser.print_help()

    @staticmethod
    def _exceed_budget(expenses: list[Expense], month: int, year: int) -> None:
        expenses_in_month = filter_by_date(expenses, month, year)
        total_expense = sum(exp.amount for exp in expenses_in_month)
        budget = load_budgets(BUDGET)[month]
        if total_expense > budget:  # type: ignore
            print(
                f"Warning: total expenses in {MONTH_NAMES[month]} {year} reaches ${total_expense},",
                f"exceeds {MONTH_NAMES[month]} budget ${budget}.",
            )

    def handle_add(self, args: Namespace) -> None:
        expenses = load_expenses(DATABASE)
        arguments = vars(args)
        arguments.pop("sub_cmd")
        new_id = expenses[-1].id + 1 if expenses else 1
        new_expense = Expense(id=new_id, **arguments)
        append_expense(DATABASE, new_expense)
        print(f"Expense added successfully (ID: {new_id})")
        self._exceed_budget(expenses + [new_expense], new_expense.create_at.month, new_expense.create_at.year)

    def handle_update(self, args: Namespace) -> None:
        updated_items = vars(args)
        updated_items.pop("sub_cmd")
        id_ = updated_items.pop("id")
        # One of --description, --amount or --category must be provided.
        if not any(updated_items.values()):
            print(
                "expense-tracker update: error: at least one of the following arguments are required:",
                "--description, --amount, --category",
            )
            return
        expenses = load_expenses(DATABASE)
        index = find_by_id(expenses, id_)
        if index is None:
            print(f"Warning: expense (ID: {id_}) does not exist.")
            return
        expenses[index].update(**updated_items)
        save_expenses(DATABASE, expenses)
        self._exceed_budget(expenses, expenses[index].create_at.month, expenses[index].create_at.year)

    def handle_delete(self, args: Namespace) -> None:
        expenses = load_expenses(DATABASE)
        index = find_by_id(expenses, args.id)
        if index is None:
            print(f"Warning: expense (ID: {args.id}) does not exist.")
            return
        expenses.pop(index)
        save_expenses(DATABASE, expenses)
        print(f"Expense (ID: {args.id}) deleted successfully.")

    def handle_list(self, args: Namespace) -> None:
        expenses = load_expenses(DATABASE)
        if args.month is not None or args.year is not None:
            expenses = filter_by_date(expenses, args.month, args.year)
        if args.category is not None:
            expenses = filter_by_category(expenses, args.category)
        # Computer max length of description and 'Description' header.
        maxlen = (
            max([len("Description")] + [len(exp.description) for exp in expenses]) if expenses else len("Description")
        )
        print(f"{'ID':4}  {'Date':10}  {'Description':{maxlen}}  {'Amount':8}  {'Category'}")
        print(f"{'--':4}  {'----':10}  {'-----------':{maxlen}}  {'------':8}  {'--------'}")
        fmt = "{id:<4}  {create_at!s:10}  {description:{width}}  ${amount:<8,}  {category}"
        for exp in expenses:
            print(fmt.format(width=maxlen, **exp.to_dict()))

    def handle_summary(self, args: Namespace) -> None:
        expenses = load_expenses(DATABASE)
        summary_category = "Total"
        if args.month is not None:
            summary_date = f" in {MONTH_NAMES[args.month]}{f' {args.year}' if args.year else ''}"
        elif args.year is not None:
            summary_date = f" in {args.year}"
        else:
            summary_date = ""
        if args.month is not None or args.year is not None:
            expenses = filter_by_date(expenses, args.month, args.year)
        if args.category is not None:
            expenses = filter_by_category(expenses, args.category)
            summary_category = args.category[0].upper() + args.category[1:]
        total = sum(exp.amount for exp in expenses)
        print(f"{summary_category} expenses{summary_date}: ${total}")

    def handle_budget(self, args: Namespace) -> None:
        budgets = load_budgets(BUDGET)
        # If --amount argument not set, print the budget for each month.
        if args.amount is None:
            print(f"{'Month':9}  {'Budget'}")
            print(f"{'-----':9}  {'------'}")
            for month in args.month:
                print(f"{MONTH_NAMES[month]:9}  {budgets[month]}")
            return
        # if --amount argument set, set a budget for each month.
        for month in args.month:
            budgets[month] = args.amount
        save_budgets(BUDGET, budgets)

    def handle_export(self, args: Namespace) -> None:
        expenses = load_expenses(DATABASE)
        save_expenses(args.csv, expenses, args.include)
