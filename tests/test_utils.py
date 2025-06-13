import json
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import pytest

# ИМПОРТЫ ИСПРАВЛЕНЫ: Обе функции импортируются из src.utils.utils
from src.utils.utils import load_operations_from_json, sort_operations_by_date


# Тесты для load_operations_from_json (из src/utils/utils.py)
def test_load_operations_from_json_valid_file_full_structure(tmp_path):
    """Тест загрузки из корректного JSON-файла с полной структурой."""
    filepath = tmp_path / "test_operations.json"
    data = [
        {  # Валидная операция
            "id": 441945886,
            "state": "EXECUTED",
            "date": "2019-08-26T10:50:58.294041Z",
            "operationAmount": {
                "amount": "31957.58",
                "currency": {"name": "руб.", "code": "RUB"},
            },
            "description": "Перевод организации",
            "from": "Maestro 1596837868705199",
            "to": "Счет 64686473678894779589",
        },
        {  # Валидная операция
            "id": 123,
            "state": "PENDING",
            "date": "2023-01-01T00:00:00.000000Z",
            "operationAmount": {
                "amount": "100.00",
                "currency": {"name": "USD", "code": "USD"},
            },
            "description": "Покупка",
            "to": "Карта 1234",
        },
        {},  # Пустой объект, должен быть отфильтрован
        {"id": 999, "description": "Неполная операция"},
        # Отсутствуют state, date, operationAmount - должен быть отфильтрован
        {
            "id": 100,
            "state": "EXECUTED",
            "date": "2023-02-01T00:00:00.000000Z",
            "description": "Без суммы",
            "operationAmount": None,  # operationAmount None - должен быть отфильтрован
        },
        {
            "id": 101,
            "state": "EXECUTED",
            "date": "2023-03-01T00:00:00.000000Z",
            "operationAmount": {"amount": "100.00", "currency": {}},
            # Отсутствует name/code в currency - должен быть отфильтрован
            "description": "Без валюты",
        },
        {
            "id": 102,
            "state": None,  # State is None - должен быть отфильтрован
            "date": "2023-04-01T00:00:00.000000Z",
            "operationAmount": {
                "amount": "50.00",
                "currency": {"name": "EUR", "code": "EUR"},
            },
            "description": "State None",
        },
        {
            "id": 103,
            "state": "EXECUTED",
            "date": "2023-05-01T00:00:00.000000Z",
            "operationAmount": {
                "amount": "50.00",
                "currency": {"name": None, "code": "EUR"},
            },
            # Currency name None - должен быть отфильтрован
            "description": "Currency name None",
        },
    ]
    filepath.write_text(json.dumps(data), encoding="utf-8")

    with patch("os.path.exists", return_value=True):
        result = load_operations_from_json(filepath)

    expected = [
        {
            "id": 441945886,
            "state": "EXECUTED",
            "date": "2019-08-26T10:50:58.294041Z",
            "operationAmount": {
                "amount": "31957.58",
                "currency": {"name": "руб.", "code": "RUB"},
            },
            "description": "Перевод организации",
            "from": "Maestro 1596837868705199",
            "to": "Счет 64686473678894779589",
        },
        {
            "id": 123,
            "state": "PENDING",
            "date": "2023-01-01T00:00:00.000000Z",
            "operationAmount": {
                "amount": "100.00",
                "currency": {"name": "USD", "code": "USD"},
            },
            "description": "Покупка",
            "to": "Карта 1234",
        },
    ]
    assert result == expected
    assert len(result) == 2


def test_load_operations_from_json_empty_file(tmp_path):
    """Тест загрузки из пустого JSON-файла."""
    filepath = tmp_path / "empty.json"
    filepath.write_text("", encoding="utf-8")
    with patch("os.path.exists", return_value=True):
        result = load_operations_from_json(filepath)
        assert result == []


def test_load_operations_from_json_invalid_json(tmp_path):
    """Тест загрузки из файла с некорректным JSON."""
    filepath = tmp_path / "invalid.json"
    filepath.write_text("not a json", encoding="utf-8")
    with patch("os.path.exists", return_value=True):
        result = load_operations_from_json(filepath)
        assert result == []


def test_load_operations_from_json_not_a_list(tmp_path):
    """Тест загрузки из файла, содержащего не список."""
    filepath = tmp_path / "not_list.json"
    data = {"key": "value"}  # Не список
    filepath.write_text(json.dumps(data), encoding="utf-8")
    with patch("os.path.exists", return_value=True):
        result = load_operations_from_json(filepath)
        assert result == []


def test_load_operations_from_json_file_not_found():
    """Тест, когда файл не найден."""
    filepath = "non_existent.json"
    with patch("os.path.exists", return_value=False):
        result = load_operations_from_json(filepath)
        assert result == []


def test_load_operations_from_json_with_none_id(tmp_path):
    """Тест загрузки JSON с операциями, где 'id' равен None."""
    filepath = tmp_path / "test_none_id.json"
    data = [
        {
            "id": 1,
            "state": "EXECUTED",
            "date": "2023-01-01T00:00:00Z",
            "operationAmount": {
                "amount": "100.00",
                "currency": {"name": "RUB", "code": "RUB"},
            },
            "description": "Op1",
        },
        {
            "id": None,
            "state": "PENDING",
            "date": "2023-01-02T00:00:00Z",  # Должна быть отфильтрована
            "operationAmount": {
                "amount": "100.00",
                "currency": {"name": "RUB", "code": "RUB"},
            },
            "description": "OpNoneId",
        },
        {
            "id": 3,
            "state": "EXECUTED",
            "date": "2023-01-03T00:00:00Z",
            "operationAmount": {
                "amount": "100.00",
                "currency": {"name": "RUB", "code": "RUB"},
            },
            "description": "Op3",
        },
    ]
    filepath.write_text(json.dumps(data), encoding="utf-8")

    with patch("os.path.exists", return_value=True):
        result = load_operations_from_json(filepath)

    expected = [
        {
            "id": 1,
            "state": "EXECUTED",
            "date": "2023-01-01T00:00:00Z",
            "operationAmount": {
                "amount": "100.00",
                "currency": {"name": "RUB", "code": "RUB"},
            },
            "description": "Op1",
        },
        {
            "id": 3,
            "state": "EXECUTED",
            "date": "2023-01-03T00:00:00Z",
            "operationAmount": {
                "amount": "100.00",
                "currency": {"name": "RUB", "code": "RUB"},
            },
            "description": "Op3",
        },
    ]
    assert result == expected
    assert len(result) == 2


# Тесты для sort_operations_by_date (из src/utils/utils.py)
def test_sort_operations_by_date_ascending():
    """Тест сортировки операций по дате в восходящем порядке (ISO формат)."""
    operations = [
        {"id": 1, "date": "2023-01-15T12:00:00Z"},
        {"id": 2, "date": "2023-01-10T12:00:00Z"},
        {"id": 3, "date": "2023-01-20T12:00:00Z"},
    ]
    sorted_ops = sort_operations_by_date(operations)
    assert [op["id"] for op in sorted_ops] == [2, 1, 3]


def test_sort_operations_by_date_descending():
    """Тест сортировки операций по дате в нисходящем порядке (ISO формат)."""
    operations = [
        {"id": 1, "date": "2023-01-15T12:00:00Z"},
        {"id": 2, "date": "2023-01-10T12:00:00Z"},
        {"id": 3, "date": "2023-01-20T12:00:00Z"},
    ]
    sorted_ops = sort_operations_by_date(operations, reverse=True)
    assert [op["id"] for op in sorted_ops] == [3, 1, 2]


def test_sort_operations_by_date_with_ddmmyyyy_format():
    """Тест сортировки операций с датами в формате DD.MM.YYYY."""
    operations = [
        {"id": 1, "date": "15.01.2023"},
        {"id": 2, "date": "10.01.2023"},
        {"id": 3, "date": "20.01.2023"},
    ]
    sorted_ops = sort_operations_by_date(operations)
    assert [op["id"] for op in sorted_ops] == [2, 1, 3]


def test_sort_operations_by_date_mixed_formats():
    """Тест сортировки операций с смешанными форматами дат."""
    operations = [
        {"id": 1, "date": "2023-01-15T12:00:00Z"},  # ISO с Z
        {"id": 2, "date": "10.01.2023"},  # DD.MM.YYYY
        {"id": 3, "date": "2023-01-20"},  # ISO без времени и Z
        {"id": 4, "date": "2023-01-05T00:00:00.000000Z"},  # ISO с Z и микросекундами
    ]
    sorted_ops = sort_operations_by_date(operations)
    # Ожидаемый порядок: 05.01 (4), 10.01 (2), 15.01 (1), 20.01 (3)
    assert [op["id"] for op in sorted_ops] == [4, 2, 1, 3]


def test_sort_operations_by_date_empty_list():
    """Тест сортировки пустого списка операций."""
    operations = []
    sorted_ops = sort_operations_by_date(operations)
    assert sorted_ops == []


def test_sort_operations_by_date_with_missing_or_empty_date():
    """Тест сортировки операций, некоторые из которых без даты или с пустой датой.
    Эти операции должны быть отфильтрованы.
    """
    operations = [
        {"id": 1, "date": "2023-01-15T12:00:00Z"},
        {"id": 2, "description": "No date"},  # Отсутствует дата - будет отфильтрована
        {"id": 3, "date": "2023-01-10T12:00:00Z"},
        {"id": 4, "date": ""},  # Пустая строка даты - будет отфильтрована
        {"id": 5, "date": None},  # Дата None - будет отфильтрована
    ]
    sorted_ops = sort_operations_by_date(operations)
    # Ожидаем только операции с валидными датами, отсортированные
    assert [op["id"] for op in sorted_ops] == [3, 1]


def test_sort_operations_by_date_invalid_date_format():
    """Тест сортировки с некорректным форматом даты.
    Эти операции должны быть отфильтрованы.
    """
    operations = [
        {"id": 1, "date": "2023-01-15T12:00:00Z"},
        {"id": 2, "date": "invalid-date"},  # Некорректный формат - будет отфильтрован
        {"id": 3, "date": "2023-01-10T12:00:00Z"},
        {"id": 4, "date": "01-01-2023"},  # Некорректный DD.MM.YYYY формат
    ]
    sorted_ops = sort_operations_by_date(operations)
    # Ожидаем только операции с валидными датами, отсортированные
    assert [op["id"] for op in sorted_ops] == [3, 1]


def test_sort_operations_by_date_all_invalid():
    """Тест сортировки, когда все даты невалидны."""
    operations = [
        {"id": 1, "date": "bad-date-1"},
        {"id": 2, "date": "bad-date-2"},
    ]
    sorted_ops = sort_operations_by_date(operations)
    assert sorted_ops == []


def test_sort_operations_by_date_with_duplicate_dates():
    """Тест сортировки операций с одинаковыми датами."""
    operations = [
        {"id": 1, "date": "2023-01-15T12:00:00Z", "order": 1},
        {"id": 2, "date": "2023-01-10T12:00:00Z", "order": 1},
        {"id": 3, "date": "2023-01-15T12:00:00Z", "order": 2},  # Дубликат даты
        {"id": 4, "date": "2023-01-20T12:00:00Z", "order": 1},
    ]
    sorted_ops = sort_operations_by_date(operations)
    # Для одинаковых дат Python сохраняет относительный порядок (стабильная сортировка)
    # Если важен порядок, то нужно добавлять вторую ключ для сортировки (например, id)
    # Но для данного теста достаточно, чтобы они были сгруппированы по дате
    assert [op["id"] for op in sorted_ops] == [2, 1, 3, 4]
