import json
import os
from unittest.mock import patch
from src.utils.utils import load_transactions_from_json
import pytest

def test_load_transactions_from_json_valid_file(tmp_path):
    """Тест загрузки из корректного JSON-файла."""
    filepath = tmp_path / "test_operations.json"
    data = [{"id": 1}, {"id": 2}]
    filepath.write_text(json.dumps(data), encoding='utf-8')
    result = load_transactions_from_json(filepath)
    assert result == data

def test_load_transactions_from_json_empty_file(tmp_path):
    """Тест загрузки из пустого JSON-файла."""
    filepath = tmp_path / "empty.json"
    filepath.write_text("", encoding='utf-8')
    result = load_transactions_from_json(filepath)
    assert result == []

def test_load_transactions_from_json_invalid_json(tmp_path):
    """Тест загрузки из файла с некорректным JSON."""
    filepath = tmp_path / "invalid.json"
    filepath.write_text("not a json", encoding='utf-8')
    result = load_transactions_from_json(filepath)
    assert result == []

def test_load_transactions_from_json_not_a_list(tmp_path):
    """Тест загрузки из файла, содержащего не список."""
    filepath = tmp_path / "not_list.json"
    data = {"key": "value"}
    filepath.write_text(json.dumps(data), encoding='utf-8')
    result = load_transactions_from_json(filepath)
    assert result == []

def test_load_transactions_from_json_file_not_found():
    """Тест, когда файл не найден."""
    filepath = "non_existent.json"
    result = load_transactions_from_json(filepath)
    assert result == []