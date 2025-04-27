import pytest

@pytest.fixture
def card_numbers():
    return [
        "1234567890123456",  # валидный
        "123456789012345",   # короткий
        "12345678901234567", # длинный
        "abcd567890123456"   # буквы
    ]

@pytest.fixture
def account_numbers():
    return [
        "1234567890",    # валидный
        "1234",          # короткий
        "abc123"         # буквы
    ]

@pytest.fixture
def transactions():
    return [
        {"state": "EXECUTED", "date": "2025-04-26T12:00:00.000"},
        {"state": "CANCELED", "date": "2024-03-10T08:30:00.000"},
        {"state": "PENDING", "date": "2024-03-11T09:45:00.000"},
        {"state": "EXECUTED", "date": "2025-04-27T14:00:00.000"}
    ]


import sys
import os

def pytest_configure(config):
    rootdir = os.path.dirname(os.path.abspath(__file__))
    src_path = os.path.join(rootdir, "src")
    sys.path.insert(0, src_path)