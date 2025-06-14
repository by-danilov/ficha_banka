import os
from unittest.mock import MagicMock, patch

import pytest
import requests
from dotenv import load_dotenv

from src.external_api.external_api import (
    get_exchange_rate,
    get_transaction_amount_in_rub,
)

load_dotenv()


@patch("requests.get")
def test_get_exchange_rate_success(mock_get):
    """Тест успешного получения обменного курса."""
    mock_response = MagicMock()
    mock_response.json.return_value = {"success": True, "rates": {"RUB": 75.0}}
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    rate = get_exchange_rate("USD")
    assert rate == 75.0
    mock_get.assert_called_once()


@patch("requests.get")
def test_get_exchange_rate_failure(mock_get):
    """Тест неудачного получения обменного курса (ошибка API)."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "success": False,
        "error": {"message": "Invalid API Key"},
    }
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    rate = get_exchange_rate("USD")
    assert rate is None
    mock_get.assert_called_once()


@patch("requests.get")
def test_get_exchange_rate_request_exception(mock_get):
    """Тест ошибки при запросе к API."""
    mock_get.side_effect = requests.exceptions.RequestException("Connection error")
    rate = get_exchange_rate("USD")
    assert rate is None
    mock_get.assert_called_once()


def test_get_transaction_amount_in_rub_rub():
    """Тест получения суммы в рублях для транзакции в рублях."""
    transaction = {"operationAmount": {"amount": "100.00", "currency": {"code": "RUB"}}}
    amount = get_transaction_amount_in_rub(transaction)
    assert amount == 100.00


@patch("src.external_api.external_api.get_exchange_rate")
def test_get_transaction_amount_in_rub_usd(mock_get_rate):
    """Тест получения суммы в рублях для транзакции в долларах."""
    mock_get_rate.return_value = 75.0
    transaction = {"operationAmount": {"amount": "10.00", "currency": {"code": "USD"}}}
    amount = get_transaction_amount_in_rub(transaction)
    assert amount == 750.0
    mock_get_rate.assert_called_once_with("USD")


@patch("src.external_api.external_api.get_exchange_rate")
def test_get_transaction_amount_in_rub_eur(mock_get_rate):
    """Тест получения суммы в рублях для транзакции в евро."""
    mock_get_rate.return_value = 80.0
    transaction = {"operationAmount": {"amount": "5.00", "currency": {"code": "EUR"}}}
    amount = get_transaction_amount_in_rub(transaction)
    assert amount == 400.0
    mock_get_rate.assert_called_once_with("EUR")


def test_get_transaction_amount_in_rub_unsupported_currency():
    """Тест для неподдерживаемой валюты."""
    transaction = {"operationAmount": {"amount": "20.00", "currency": {"code": "GBP"}}}
    amount = get_transaction_amount_in_rub(transaction)
    assert amount is None


def test_get_transaction_amount_in_rub_no_operation_amount():
    """Тест при отсутствии ключа 'operationAmount'."""
    transaction = {}
    amount = get_transaction_amount_in_rub(transaction)
    assert amount is None


def test_get_transaction_amount_in_rub_missing_data():
    """Тест при отсутствии 'amount' или 'currency'."""
    transaction1 = {"operationAmount": {"currency": {"code": "RUB"}}}
    transaction2 = {"operationAmount": {"amount": "100.00"}}
    assert get_transaction_amount_in_rub(transaction1) is None
    assert get_transaction_amount_in_rub(transaction2) is None
