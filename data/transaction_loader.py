import csv
import logging
import os

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

file_handler = logging.FileHandler(
    os.path.join(log_dir, "data_loader.log"), mode="w", encoding="utf-8"
)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


def load_transactions_from_csv(file_path: str) -> list[dict]:
    """
    Загружает данные о банковских операциях из CSV-файла.

    Ожидает, что CSV-файл имеет заголовки 'id', 'description', 'amount', 'currency', 'date', 'status', 'from', 'to'.
    Поле 'amount' будет преобразовано в float.
    Поле 'id' будет преобразовано в int.

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
        with open(file_path, mode="r", newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            # Обновленный список обязательных полей
            required_headers = [
                "id",
                "description",
                "amount",
                "currency",
                "date",
                "status",
                "from",
                "to",
            ]
            if not all(header in reader.fieldnames for header in required_headers):
                logger.error(
                    f"Отсутствуют обязательные заголовки в CSV-файле: {required_headers}. Найдено: {reader.fieldnames}"
                )
                return []

            for row in reader:
                try:
                    transaction = {
                        "id": int(row["id"]),
                        "description": row["description"],
                        "amount": float(row["amount"]),
                        "currency": row["currency"],
                        "date": row["date"],  # Добавлено
                        "status": row["status"],  # Добавлено
                        "from": row.get(
                            "from", ""
                        ),  # Добавлено, используем .get() на случай отсутствия
                        "to": row.get(
                            "to", ""
                        ),  # Добавлено, используем .get() на случай отсутствия
                    }
                    transactions.append(transaction)
                except (ValueError, KeyError) as e:
                    logger.warning(
                        f"Пропущена строка из-за некорректных данных: {row}. Ошибка: {e}"
                    )
            logger.info(
                f"Успешно загружено {len(transactions)} транзакций из {file_path}."
            )
    except Exception as e:
        logger.error(f"Ошибка при чтении CSV файла {file_path}: {e}")
        transactions = []
    return transactions


if __name__ == "__main__":
    # Пример использования (можно удалить в финальной версии, но полезно для тестирования)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Путь к data/transactions.csv относительно корня проекта
    csv_path = os.path.join(current_dir, "..", "..", "data", "transactions.csv")

    print(f"Попытка загрузки из: {csv_path}")
    loaded_transactions = load_transactions_from_csv(csv_path)
    if loaded_transactions:
        print(f"Загружено {len(loaded_transactions)} транзакций.")
        for tx in loaded_transactions[:3]:  # Вывести первые 3 для примера
            print(tx)
    else:
        print("Не удалось загрузить транзакции.")
