import json
import os

def load_transactions_from_json(filepath):
    """
    Загружает данные о финансовых транзакциях из JSON-файла.

    Args:
        filepath (str): Путь до JSON-файла.

    Returns:
        list: Список словарей с данными о транзакциях.
              Возвращает пустой список, если файл не найден, пуст или содержит не список.
    """
    if not os.path.exists(filepath):
        return []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            else:
                return []
    except json.JSONDecodeError:
        return []
    except FileNotFoundError:
        return []

if __name__ == '__main__':
    # Пример использования (при наличии файла data/operations.json)
    operations_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'operations.json')
    transactions = load_transactions_from_json(operations_file)
    print(f"Загружено транзакций: {len(transactions)}")
    if transactions:
        print(f"Первая транзакция: {transactions[0]}")