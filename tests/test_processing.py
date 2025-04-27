import pytest
from processing import filter_by_state, sort_by_date

def test_filter_by_state_executed(transactions):
    result = filter_by_state(transactions, state="EXECUTED")
    assert all(tx["state"] == "EXECUTED" for tx in result)

def test_filter_by_state_none_found(transactions):
    result = filter_by_state(transactions, state="UNKNOWN")
    assert result == []

@pytest.mark.parametrize("state", ["EXECUTED", "CANCELED", "PENDING"])
def test_filter_by_state_various(transactions, state):
    result = filter_by_state(transactions, state=state)
    for tx in result:
        assert tx["state"] == state

def test_sort_by_date_descending(transactions):
    sorted_data = sort_by_date(transactions)
    dates = [tx["date"] for tx in sorted_data]
    assert dates == sorted(dates, reverse=True)

def test_sort_by_date_ascending(transactions):
    sorted_data = sort_by_date(transactions, descending=False)
    dates = [tx["date"] for tx in sorted_data]
    assert dates == sorted(dates)
