import pytest

from src.generators import (
    card_number_generator,
    filter_by_currency,
    transaction_descriptions,
)


@pytest.fixture
def sample_transactions():
    return [
        {
            "id": 1,
            "operationAmount": {"currency": {"code": "USD"}},
            "description": "USD Payment",
        },
        {
            "id": 2,
            "operationAmount": {"currency": {"code": "RUB"}},
            "description": "RUB Payment",
        },
        {
            "id": 3,
            "operationAmount": {"currency": {"code": "USD"}},
            "description": "Second USD Payment",
        },
    ]


def test_filter_by_currency_usd(sample_transactions):
    gen = filter_by_currency(sample_transactions, "USD")
    result = list(gen)
    assert len(result) == 2
    assert all(t["operationAmount"]["currency"]["code"] == "USD" for t in result)


def test_filter_by_currency_none_found(sample_transactions):
    gen = filter_by_currency(sample_transactions, "EUR")
    assert list(gen) == []


def test_filter_by_currency_empty_list():
    assert list(filter_by_currency([], "USD")) == []


def test_transaction_descriptions(sample_transactions):
    gen = transaction_descriptions(sample_transactions)
    descriptions = list(gen)
    assert descriptions == ["USD Payment", "RUB Payment", "Second USD Payment"]


def test_transaction_descriptions_empty():
    assert list(transaction_descriptions([])) == []


@pytest.mark.parametrize(
    "start,end,expected",
    [
        (1, 1, ["0000 0000 0000 0001"]),
        (1, 3, ["0000 0000 0000 0001", "0000 0000 0000 0002", "0000 0000 0000 0003"]),
    ],
)
def test_card_number_generator(start, end, expected):
    result = list(card_number_generator(start, end))
    assert result == expected
