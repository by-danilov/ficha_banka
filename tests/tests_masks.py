import pytest
from src.masks import get_mask_card_number, get_mask_account


@pytest.mark.parametrize("card_number,expected", [
    ("1234567890123456", "1234 56** **** 3456")
])
def test_get_mask_card_number_valid(card_number, expected):
    assert get_mask_card_number(card_number) == expected


@pytest.mark.parametrize("card_number", ["123456789012345",   # короткий
                                         "12345678901234567",  # длинный
                                         "abcd567890123456"   # буквы
                                         ])
def test_get_mask_card_number_invalid(card_number):
    with pytest.raises(ValueError):
        get_mask_card_number(card_number)


@pytest.mark.parametrize("account_number,expected", [
    ("1234567890", "**7890")
])
def test_get_mask_account_valid(account_number, expected):
    assert get_mask_account(account_number) == expected


@pytest.mark.parametrize("account_number", [
    "1234", "abc123"
])
def test_get_mask_account_invalid(account_number):
    with pytest.raises(ValueError):
        get_mask_account(account_number)
