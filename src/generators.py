def filter_by_currency(transactions, currency_code):
    """Генератор, фильтрующий транзакции по валюте."""
    for transaction in transactions:
        if (
            transaction.get("operationAmount", {}).get("currency", {}).get("code")
            == currency_code
        ):
            yield transaction


def transaction_descriptions(transactions):
    """Генератор, возвращающий описания транзакций."""
    for transaction in transactions:
        yield transaction.get("description", "")


def card_number_generator(start, end):
    """Генератор номеров карт в формате XXXX XXXX XXXX XXXX."""
    for num in range(start, end + 1):
        formatted = f"{num:016}"
        yield f"{formatted[:4]} {formatted[4:8]} {formatted[8:12]} {formatted[12:]}"
