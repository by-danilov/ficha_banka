import logging
import json
import os
from datetime import datetime

# Создаем логгер для модуля utils
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Создаем обработчик для записи логов в файл
log_dir = 'logs'
os.makedirs(log_dir, exist_ok=True)
file_handler = logging.FileHandler(os.path.join(log_dir, 'utils.log'), mode='w', encoding='utf-8')
# Создаем форматтер
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
# Добавляем обработчик к логгеру
logger.addHandler(file_handler)


def load_operations(file_path: str) -> list[dict]:
    """
    Загружает данные о банковских операциях из JSON-файла с валидацией и приведением типов,
    учитывая вложенную структуру operationAmount и ключ state.
    Args:
        file_path (str): Полный путь к JSON-файлу.
    Returns:
        list[dict]: Список словарей, где каждый словарь представляет одну транзакцию.
                    Возвращает пустой список, если файл не найден или произошла ошибка.
    """
    transactions = []
    if not os.path.exists(file_path):
        logger.error(f"Файл не найден: {file_path}")
        return []
    try:
        with open(file_path, 'r', encoding='utf-8') as jsonfile:
            data = json.load(jsonfile)
            if not isinstance(data, list):
                logger.error(f"JSON-файл {file_path} содержит некорректный формат (ожидается список).")
                return []

            for i, row in enumerate(data):
                # Пропускаем пустые словари, которые могут встречаться
                if not row:
                    logger.warning(f"Пустой объект найден в JSON-файле {file_path} на позиции {i}. Пропущен.")
                    continue

                if not isinstance(row, dict):
                    logger.warning(f"Элемент {i + 1} в JSON-файле {file_path} не является словарем. Пропущен.")
                    continue

                # Проверяем наличие обязательных верхнеуровневых ключей
                required_top_level_keys = ['id', 'state', 'date', 'operationAmount', 'description']
                if not all(key in row for key in required_top_level_keys):
                    missing_keys = [key for key in required_top_level_keys if key not in row]
                    logger.warning(
                        f"Элемент {i + 1} в JSON-файле {file_path} не содержит все обязательные верхнеуровневые ключи {missing_keys}. Пропущен: {row}")
                    continue

                operation_amount = row.get('operationAmount', {})
                currency_info = operation_amount.get('currency', {})

                # Проверяем наличие обязательных вложенных ключей в operationAmount и currency
                if 'amount' not in operation_amount or 'name' not in currency_info:
                    logger.warning(
                        f"Элемент {i + 1} в JSON-файле {file_path} не содержит необходимые вложенные поля (amount в operationAmount или name в currency). Пропущен: {row}")
                    continue

                try:
                    # Преобразование даты из "YYYY-MM-DDTHH:MM:SS.microseconds" в "DD.MM.YYYY"
                    date_obj = datetime.fromisoformat(row['date'].replace('Z', '+00:00'))
                    formatted_date = date_obj.strftime('%d.%m.%Y')

                    transaction = {
                        'id': int(row['id']),
                        'description': str(row['description']),
                        'amount': float(operation_amount['amount']),
                        'currency': str(currency_info['name']),
                        'date': formatted_date,
                        'status': str(row['state']),
                        'from': str(row.get('from', '')),
                        'to': str(row.get('to', ''))
                    }
                    transactions.append(transaction)
                except (ValueError, KeyError, TypeError) as e:
                    logger.warning(
                        f"Пропущена строка {i + 1} из-за некорректных данных или ошибки приведения типов: {row}. Ошибка: {e}")
        logger.info(f"Успешно загружено {len(transactions)} транзакций из {file_path}.")
    except json.JSONDecodeError as e:
        logger.error(f"Ошибка при декодировании JSON файла {file_path}: {e}")
        transactions = []
    except Exception as e:
        logger.error(f"Произошла непредвиденная ошибка при чтении JSON файла {file_path}: {e}")
        transactions = []
    return transactions


def sort_operations_by_date(operations: list[dict], reverse: bool = False) -> list[dict]:
    """Сортирует список операций по дате. Ожидает дату в формате 'DD.MM.YYYY'."""
    if not isinstance(operations, list):
        logger.warning("Передан некорректный тип данных для сортировки операций.")
        return operations
    try:
        sorted_ops = sorted(
            operations,
            key=lambda x: datetime.strptime(x.get('date', '01.01.1900'), '%d.%m.%Y') if x.get('date') else datetime(
                1900, 1, 1),
            reverse=reverse
        )
        logger.debug(f"Операции отсортированы по дате (reverse={reverse}). Количество операций: {len(sorted_ops)}")
        return sorted_ops
    except ValueError as e:
        logger.error(f"Ошибка формата даты при сортировке: {e}. Проверьте формат даты в данных.")
        return operations
    except Exception as e:
        logger.error(f"Произошла ошибка при сортировке операций: {e}")
        return operations


if __name__ == '__main__':
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(current_dir, '..', '..', 'data', 'operations.json')

    print(f"Попытка загрузки из: {json_path}")
    operations = load_operations(json_path)
    if operations:
        print(f"Загружено {len(operations)} операций.")
        for i, op in enumerate(operations[:5]):
            print(
                f"  Op {i + 1}: ID={op.get('id')}, Date={op.get('date')}, Amount={op.get('amount')} {op.get('currency')}, Status={op.get('status')}")

        sorted_operations = sort_operations_by_date(operations, reverse=True)
        if sorted_operations:
            print(f"\nПервая отсортированная операция: {sorted_operations[0].get('date')}")
        else:
            print("Список отсортированных операций пуст.")
    else:
        print("Не удалось загрузить операции.")