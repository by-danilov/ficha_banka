import os

import requests
from dotenv import load_dotenv

load_dotenv()
EXCHANGE_RATES_API_KEY = os.getenv("EXCHANGE_RATES_API_KEY")
BASE_URL = "https://api.apilayer.com/exchangerates_data/"


def get_exchange_rate(from_currency, to_currency="RUB"):
    """
    Получает текущий обменный курс валюты с помощью Exchange Rates Data API.

    Args:
        from_currency (str): Код валюты, которую нужно конвертировать (например, 'USD').
        to_currency (str, optional): Код валюты, в которую нужно конвертировать (по умолчанию 'RUB').

    Returns:
        float: Текущий обменный курс или None в случае ошибки.
    """
    if not EXCHANGE_RATES_API_KEY:
        print("Ошибка: Не найден API-ключ для Exchange Rates Data API в .env")
        return None

    url = f"{BASE_URL}latest?symbols={to_currency}&base={from_currency}"
    headers = {"apikey": EXCHANGE_RATES_API_KEY}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()
        if data and data.get("success"):
            rates = data.get("rates")
            return rates.get(to_currency)
        else:
            print(f"Ошибка API: {data.get('error')}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе к API: {e}")
        return None
    except KeyError:
        print("Ошибка: Неверный формат ответа от API.")
        return None


def get_transaction_amount_in_rub(transaction):
    """
    Возвращает сумму транзакции в рублях.

    Args:
        transaction (dict): Словарь с данными о транзакции.

    Returns:
        float: Сумма транзакции в рублях.
               Возвращает None, если не удалось определить или конвертировать сумму.
    """
    operation_amount = transaction.get("operationAmount")
    if not operation_amount:
        return None

    amount_str = operation_amount.get("amount")
    currency_info = operation_amount.get("currency")

    if not amount_str or not currency_info:
        return None

    try:
        amount = float(amount_str)
        currency_code = currency_info.get("code")

        if currency_code == "RUB":
            return amount
        elif currency_code in ["USD", "EUR"]:
            exchange_rate = get_exchange_rate(currency_code)
            if exchange_rate is not None:
                return amount * exchange_rate
            else:
                print(f"Не удалось получить курс {currency_code} к RUB.")
                return None
        else:
            print(f"Неподдерживаемая валюта: {currency_code}")
            return None
    except ValueError:
        print(f"Некорректное значение суммы: {amount_str}")
        return None


if __name__ == "__main__":
    # Пример использования (требуется наличие EXCHANGE_RATES_API_KEY в .env)
    test_transaction_rub = {
        "operationAmount": {"amount": "100.00", "currency": {"code": "RUB"}}
    }
    test_transaction_usd = {
        "operationAmount": {"amount": "10.00", "currency": {"code": "USD"}}
    }
    print(
        f"Сумма в рублях (RUB): {get_transaction_amount_in_rub(test_transaction_rub)}"
    )
    print(
        f"Сумма в рублях (USD): {get_transaction_amount_in_rub(test_transaction_usd)}"
    )
