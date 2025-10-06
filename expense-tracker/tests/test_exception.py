import pytest
from expense_tracker import main


@pytest.mark.parametrize("exception", [KeyboardInterrupt, Exception("fail")])
def test_exception(monkeypatch, exception):
    class DummyCLI:
        def __init__(self):
            raise exception

    monkeypatch.setattr("expense_tracker.cli.CLI", DummyCLI)
    result = main()
    assert result == 1
