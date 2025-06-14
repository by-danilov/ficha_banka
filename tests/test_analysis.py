# tests/test_analysis.py
from collections import Counter

import pytest

from src.analysis.additional_analytics import (
    count_transactions_by_category,
    find_transactions_by_description,
)


# Фикстура с тестовыми данными для транзакций (используем латиницу!)
@pytest.fixture
def sample_transactions():
    return [
        {"id": 1, "description": "Transfer to client", "amount": 100},
        {"id": 2, "description": "Groceries purchase at store", "amount": 200},
        {"id": 3, "description": "Transfer from Vasya", "amount": 50},
        {"id": 4, "description": "Communication services payment", "amount": 300},
        {"id": 5, "description": "money transfer", "amount": 70},
        {
            "id": 6,
            "description": "Refund for purchase",
            "amount": 150,
        },  # Здесь "purchase"
    ]


# --- Тесты для find_transactions_by_description ---


def test_find_transactions_by_description_success(sample_transactions):
    """Тест успешного поиска транзакций по описанию (без учета регистра)."""
    search_string = "transfer"
    result = find_transactions_by_description(sample_transactions, search_string)
    expected = [
        {"id": 1, "description": "Transfer to client", "amount": 100},
        {"id": 3, "description": "Transfer from Vasya", "amount": 50},
        {"id": 5, "description": "money transfer", "amount": 70},
    ]
    assert result == expected


def test_find_transactions_by_description_no_match(sample_transactions):
    """Тест поиска, когда совпадений не найдено."""
    search_string = "taxi"
    result = find_transactions_by_description(sample_transactions, search_string)
    assert result == []


def test_find_transactions_by_description_empty_search_string(sample_transactions):
    """Тест поиска с пустой строкой поиска (должны вернуться все транзакции)."""
    search_string = ""
    result = find_transactions_by_description(sample_transactions, search_string)
    assert result == sample_transactions


def test_find_transactions_by_description_empty_transactions_list():
    """Тест поиска с пустым списком транзакций."""
    search_string = "purchase"
    result = find_transactions_by_description([], search_string)
    assert result == []


def test_find_transactions_by_description_case_insensitivity(sample_transactions):
    """Тест поиска с учетом регистра (должен работать без учета)."""
    search_string = "TRANSFER"
    result = find_transactions_by_description(sample_transactions, search_string)
    expected = [
        {"id": 1, "description": "Transfer to client", "amount": 100},
        {"id": 3, "description": "Transfer from Vasya", "amount": 50},
        {"id": 5, "description": "money transfer", "amount": 70},
    ]
    assert result == expected


def test_find_transactions_by_description_with_regex_characters(sample_transactions):
    """Тест поиска с использованием специальных символов регулярных выражений."""
    # Поиск "purchase" + любые символы после
    search_string = "purchase.*"
    result = find_transactions_by_description(sample_transactions, search_string)
    expected = [
        {"id": 2, "description": "Groceries purchase at store", "amount": 200},
        {
            "id": 6,
            "description": "Refund for purchase",
            "amount": 150,
        },  # Теперь ожидаем, что найдет и эту
    ]
    assert result == expected


def test_find_transactions_by_description_invalid_regex():
    """Тест поиска с некорректным регулярным выражением."""
    transactions = [{"id": 1, "description": "Test description"}]
    search_string = "["  # Некорректное регулярное выражение
    result = find_transactions_by_description(transactions, search_string)
    assert result == []  # Функция должна обработать ошибку и вернуть пустой список


# --- Тесты для count_transactions_by_category ---


def test_count_transactions_by_category_success(sample_transactions):
    """Тест успешного подсчета категорий."""
    categories = ["transfer", "purchase", "services"]
    result = count_transactions_by_category(sample_transactions, categories)
    expected = {
        "transfer": 3,
        "purchase": 2,  # 'Groceries purchase' и 'Refund for purchase'
        "services": 1,
    }
    assert result == expected


def test_count_transactions_by_category_no_match(sample_transactions):
    """Тест подсчета, когда ни одна транзакция не попадает в категории."""
    categories = ["taxi", "restaurant"]
    result = count_transactions_by_category(sample_transactions, categories)
    expected = {"taxi": 0, "restaurant": 0}
    assert result == expected


def test_count_transactions_by_category_empty_transactions_list():
    """Тест подсчета с пустым списком транзакций."""
    categories = ["transfer", "purchase"]
    result = count_transactions_by_category([], categories)
    expected = {"transfer": 0, "purchase": 0}
    assert result == expected


def test_count_transactions_by_category_empty_categories_list(sample_transactions):
    """Тест подсчета с пустым списком категорий."""
    categories = []
    result = count_transactions_by_category(sample_transactions, categories)
    assert result == {}


def test_count_transactions_by_category_case_insensitivity(sample_transactions):
    """Тест подсчета с учетом регистра категорий."""
    categories = ["TRANSFER", "Purchase"]
    result = count_transactions_by_category(sample_transactions, categories)
    expected = {"TRANSFER": 3, "Purchase": 2}  # Ожидаем, что найдет 2
    assert result == expected


def test_count_transactions_by_category_multiple_matches_in_one_transaction():
    """
    Тест, когда одна транзакция содержит несколько ключевых слов категорий.
    Она должна быть учтена для каждой категории.
    """
    transactions = [
        {
            "id": 1,
            "description": "Payment for services related to transfer",
            "amount": 100,
        }
    ]
    categories = ["services", "transfer"]
    result = count_transactions_by_category(transactions, categories)
    expected = {"services": 1, "transfer": 1}
    assert result == expected
