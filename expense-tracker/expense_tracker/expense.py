from dataclasses import dataclass, field, fields
from datetime import date
from typing import Any, Callable


@dataclass(slots=True)
class Expense:
    id: int
    description: str
    amount: float
    category: str
    create_at: date = field(default_factory=date.today)

    def update(self, description: str | None = None, amount: float | None = None, category: str | None = None) -> None:
        if description is not None:
            self.description = description
        if amount is not None:
            self.amount = amount
        if category is not None:
            self.category = category

    @classmethod
    def fields(cls) -> tuple[str, ...]:
        return tuple(field_.name for field_ in fields(Expense))

    def to_tuple(self) -> tuple[int, str, float, date]:
        return tuple(getattr(self, field_.name) for field_ in fields(Expense))

    def to_dict(self) -> dict:
        return {field_.name: getattr(self, field_.name) for field_ in fields(Expense)}


def filter_by_category(expenses: list[Expense], category: str) -> list[Expense]:
    """Filter expenses by category.

    Args:
        expenses (list[Expense]): A list of Expense objects.
        category (str): The category of expenses that are searched.

    Returns:
        list[Expense]: A list of Expense objects for a category.
    """
    return [exp for exp in expenses if exp.category == category]


def filter_by_date(expenses: list[Expense], month: int, year: int | None = None) -> list[Expense]:
    """Filter expenses by the month or year that the expenses are created in.
    The date when expense created is in non-decreasing order, binary search algorithm
    can be used to find the index of the first and last expense that created in a month or year.

    Args:
        expenses (list[Expense]): A list of Expense objects.
        month (int | None): The month that the searched expenses are created in.
            If it is None, then filter by a year (the year should not be None).
        year (int | None, optional): The year that the searched expenses are created in.
            If the month isn't None but the year is None, then set the year as the current year.
            Defaults to None.

    Returns:
        list[Expense]: A list of Expense objects that created in a month or a year.

    Raises:
        TypeError: If month and year are all None, raise TypeError.
    """

    def year_and_month(exp: Expense) -> tuple[int, int]:
        return (exp.create_at.year, exp.create_at.month)

    length = len(expenses)
    if month is None:
        if year is None:
            raise TypeError("One of the following arguments must be provided: month, year.")

        # filter by a year
        start = _first_ge_index(expenses, (year, 1), 0, length, year_and_month)
        stop = _first_ge_index(expenses, (year + 1, 1), start, length, year_and_month)
    else:
        if year is None:
            year = date.today().year
        start = _first_ge_index(expenses, (year, month), 0, length, year_and_month)
        # It's OK even if month is 12.
        stop = _first_ge_index(expenses, (year, month + 1), start, length, year_and_month)
    return expenses[start:stop]


def find_by_id(expenses: list[Expense], id_: int) -> int | None:
    """Find an expense which its ID is id_ from a list of Expense objects, return its index if success,
    otherwise return None.
    The expense id is non-decreasing order, binary search algorithm can be used to find its index.

    Args:
        expenses (list[Expense]): A list of Expense objects.
        id_ (int): ID of the expense to find.

    Returns:
        int | None: Index of the expense in the list, or None if not in.
    """
    length = len(expenses)
    index = _first_ge_index(expenses, id_, 0, length, key=lambda x: x.id)
    if index == length or expenses[index].id != id_:
        return None
    return index


def _first_ge_index(seq: list[Expense], target: Any, low: int, high: int, key: Callable[[Expense], Any]) -> int:
    """
    Use binary search to find the index of the first element in a sequence that is greater than or equal to a given value.

    Args:
        seq (list[Expense]): A list of Expense objects to search, which should be sorted by key.
        target (Any): The target value to compare.
        low (int): The start index of search range.
        high (int): The stop index of search range.
        key (Callable[[Expense], Any]): A function with one argument that is used to extract a comparison key from each element.

    Returns:
        int: The index of the first element greater than or equal to target. Returns len(seq) if not found.
    """
    while low < high:
        mid = low + high >> 1
        if key(seq[mid]) < target:
            low = mid + 1
        else:
            high = mid
    return low
