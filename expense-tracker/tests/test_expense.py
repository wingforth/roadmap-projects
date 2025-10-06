import pytest
from datetime import date
from expense_tracker.expense import (
    Expense,
    filter_by_category,
    filter_by_date,
    find_by_id,
    _first_ge_index,
)


@pytest.mark.parametrize(
    "category, excepted",
    [
        # 正常类别
        (
            "Food",
            [
                Expense(1, "Lunch", 15.0, "Food", date(2024, 7, 1)),
                Expense(2, "Dinner", 28.5, "Food", date(2025, 3, 2)),
                Expense(6, "Coffee", 8.0, "Food", date(2025, 5, 6)),
            ],
        ),
        # 不存在类别
        ("NonExist", []),
    ],
)
def test_filter_by_category(init_expenses, category, excepted):
    assert filter_by_category(init_expenses, category) == excepted


def test_filter_by_category_empty():
    # 空列表
    assert filter_by_category([], "Food") == []


@pytest.mark.parametrize(
    "month, year, excepted",
    [
        (
            5,
            2025,
            [
                Expense(5, "Movie", 30.0, "Entertainment", date(2025, 5, 5)),
                Expense(6, "Coffee", 8.0, "Food", date(2025, 5, 6)),
            ],
        ),
        # not provide year
        (
            7,
            None,
            [
                Expense(9, "Taxi", 25.0, "Transport", date(2025, 7, 2)),
                Expense(10, "Notebook", 12.0, "Education", date(2025, 7, 15)),
            ],
        ),
        # not this year
        (
            7,
            2024,
            [
                Expense(1, "Lunch", 15.0, "Food", date(2024, 7, 1)),
            ],
        ),
        # filter by a year
        (
            None,
            2024,
            [
                Expense(1, "Lunch", 15.0, "Food", date(2024, 7, 1)),
            ],
        ),
        # 无数据月份
        (2, None, []),
        # 无数据年份
        (6, 2023, []),
    ],
)
def test_filter_by_month(init_expenses, month, year, excepted):
    assert filter_by_date(init_expenses, month, year) == excepted


def test_filter_by_month_empty():
    # 空列表
    assert filter_by_date([], 1, 2024) == []


@pytest.mark.parametrize("id_, expected", [(1, 0), (2, 1), (10, 9), (99, None), (0, None)])
def test_find_by_id(init_expenses, id_, expected):
    assert find_by_id(init_expenses, id_) == expected


def test_find_by_id_empty():
    assert find_by_id([], 1) is None


@pytest.mark.parametrize(
    "seq, target, low, high, key, expected",
    [
        # 找到目标值
        ([1, 2, 3, 4, 5], 3, 0, 5, lambda x: x, 2),
        ([1, 2, 4, 5, 6], 3, 0, 5, lambda x: x, 2),
        # 未找到目标值
        ([1, 2, 3, 4, 5], 6, 0, 5, lambda x: x, 5),
        ([1, 2, 3, 4, 5], 0, 0, 5, lambda x: x, 0),
        # 空序列
        ([], 3, 0, 0, lambda x: x, 0),
        # 单元素序列
        ([3], 3, 0, 1, lambda x: x, 0),
        # 非整数键
        ([(1, 2), (3, 4), (5, 6), (6, 7), (8, 9)], (4, 5), 0, 5, lambda x: x, 2),
        # 自定义键
        ([{"value": 1}, {"value": 2}, {"value": 3}, {"value": 4}, {"value": 5}], 3, 0, 5, lambda x: x["value"], 2),
        # 边界测试
        ([1, 2, 3], 4, 0, 3, lambda x: x, 3),
        ([1, 2, 3], 1, 0, 3, lambda x: x, 0),
    ],
)
def test_first_ge_index(seq, target, low, high, key, expected):
    result = _first_ge_index(seq, target, low, high, key)
    assert result == expected
