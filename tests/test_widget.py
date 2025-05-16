import pytest

from src.widget import get_date, mask_input_string


@pytest.mark.parametrize("input_data,expected", [
    ("Карта 1234567890123456", "Карта 1234 56** **** 3456"),
    ("Счет 1234567890", "Счет **7890"),
])
def test_mask_input_string_valid(input_data, expected):
    assert mask_input_string(input_data) == expected


@pytest.mark.parametrize("input_data", [
    "НеверныйФормат",
    "Просто текст"
])
def test_mask_input_string_invalid(input_data):
    with pytest.raises(ValueError):
        mask_input_string(input_data)


@pytest.mark.parametrize("date_str,expected", [
    ("2025-04-27T15:30:00.000", "27.04.2025"),
    ("2023-01-01T00:00:00.000", "01.01.2023")
])
def test_get_date_valid(date_str, expected):
    assert get_date(date_str) == expected
