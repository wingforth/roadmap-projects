import pytest
from argparse import ArgumentTypeError
from expense_tracker.commands import _non_negative_float


@pytest.mark.parametrize("numstr, expected", [("0", 0.0), ("123.45", 123.45), ("20", 20), ("inf", float("inf"))])
def test_non_negative_float_valid(numstr, expected):
    assert _non_negative_float(numstr) == expected


@pytest.mark.parametrize("numstr", ["-1", "abc", "4a", "-inf"])
def test_non_negative_float_invalid(numstr):
    with pytest.raises(ArgumentTypeError):
        _non_negative_float(numstr)
