# src/data/transaction_loader.py
import csv
import os
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Убедимся, что папка logs существует
log_dir = 'logs'
os.makedirs(log_dir, exist_ok=True)

# Настройка файлового обработчика для записи логов в файл
file_handler = logging.FileHandler(os.path.join(log_dir, 'data_loader.log'), mode='w')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


def load_transactions_from_csv(file_path: str) -> list[dict]:
    """
    Загружает данные о банковских операциях из CSV-файла.

    Ожидает, что CSV-файл имеет заголовки 'id', 'description', 'amount', 'currency'.
    Поле 'amount' будет преобразовано в float.

    Args:
        file_path (str): Полный путь к CSV-файлу.

    Returns:
        list[dict]: Список словарей, где каждый словарь представляет одну транзакцию.
                    Возвращает пустой список, если файл не найден или произошла ошибка.
    """
    transactions = []
    if not os.path.exists(file_path):
        logger.error(f"Файл не найден: {file_path}")
        return []

    try:
        with open(file_path, mode='r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            # Проверка обязательных полей
            required_headers = ['id', 'description', 'amount', 'currency']
            if not all(header in reader.fieldnames for header in required_headers):
                logger.error(f"Отсутствуют обязательные заголовки в CSV-файле: {required_headers}. Найдено: {reader.fieldnames}")
                return []

            for row in reader:
                try:
                    # Преобразование id и amount к нужным типам
                    transaction = {
                        'id': int(row['id']),
                        'description': row['description'],
                        'amount': float(row['amount']),
                        'currency': row['currency']
                    }
                    transactions.append(transaction)
                except (ValueError, KeyError) as e:
                    logger.warning(f"Пропущена строка из-за некорректных данных: {row}. Ошибка: {e}")
        logger.info(f"Успешно загружено {len(transactions)} транзакций из {file_path}.")
    except Exception as e:
        logger.error(f"Ошибка при чтении CSV файла {file_path}: {e}")
        transactions = []
    return transactions
        