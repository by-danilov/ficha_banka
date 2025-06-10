# src/analysis/transaction_analyzer.py
import logging
import os
import re
from collections import Counter

# Настройка логгера для модуля
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

log_dir = 'logs'
os.makedirs(log_dir, exist_ok=True)
file_handler = logging.FileHandler(os.path.join(log_dir, 'analysis.log'), mode='w')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

def find_transactions_by_description(transactions: list[dict], search_string: str) -> list[dict]:
    """
    Фильтрует список банковских операций, возвращая те, у которых в описании
    (поле 'description') содержится заданная строка поиска.

    Поиск выполняется с использованием регулярных выражений, без учета регистра.

    Args:
        transactions (list[dict]): Список словарей с данными о банковских операциях.
                                   Каждый словарь должен содержать ключ 'description'.
        search_string (str): Строка или регулярное выражение для поиска в описании.

    Returns:
        list[dict]: Отфильтрованный список словарей, соответствующих условию поиска.
    """
    if not transactions:
        logger.warning("Передан пустой список транзакций для поиска по описанию.")
        return []

    if not search_string:
        logger.warning("Передана пустая строка поиска для описания. Возвращены все транзакции.")
        return transactions

    filtered_transactions = []
    try:
        # Компилируем регулярное выражение для более эффективного поиска
        # re.IGNORECASE для поиска без учета регистра
        pattern = re.compile(search_string, re.IGNORECASE)
        for transaction in transactions:
            description = transaction.get('description', '')
            if pattern.search(description):
                filtered_transactions.append(transaction)
        logger.info(f"Найдено {len(filtered_transactions)} транзакций с описанием, содержащим '{search_string}'.")
    except re.error as e:
        logger.error(f"Некорректное регулярное выражение '{search_string}': {e}. Возвращен пустой список.")
        return []
    except Exception as e:
        logger.error(f"Произошла непредвиденная ошибка при поиске по описанию: {e}")
        return []
    return filtered_transactions


def count_transactions_by_category(transactions: list[dict], categories: list[str]) -> dict:
    """
    Подсчитывает количество операций для каждой заданной категории.

    Категории определяются наличием одного из слов из списка `categories`
    в поле 'description' транзакции (без учета регистра).

    Args:
        transactions (list[dict]): Список словарей с данными о банковских операциях.
                                   Каждый словарь должен содержать ключ 'description'.
        categories (list[str]): Список строк, представляющих категории (ключевые слова).

    Returns:
        dict: Словарь, где ключи — это названия категорий (из `categories`),
              а значения — количество операций, соответствующих этой категории.
              Если транзакция подходит под несколько категорий, она будет учтена
              в каждой из них.
    """
    if not transactions:
        logger.warning("Передан пустой список транзакций для подсчета категорий.")
        return {cat: 0 for cat in categories}

    if not categories:
        logger.warning("Передан пустой список категорий для подсчета.")
        return {}

    category_counts = Counter()

    for transaction in transactions:
        description = transaction.get('description', '')
        if description:
            # Преобразуем описание к нижнему регистру один раз для сравнения
            lower_description = description.lower()
            for category_name in categories:
                # Теперь ищем категорию как подстроку в описании без использования re
                # Так как по условию re нужен только для первой функции
                if category_name.lower() in lower_description:
                    category_counts[category_name] += 1

    # Убедимся, что все запрошенные категории присутствуют в словаре, даже если их count=0
    for cat in categories:
        if cat not in category_counts:
            category_counts[cat] = 0

    logger.info(f"Подсчет категорий завершен. Результат: {dict(category_counts)}")
    return dict(category_counts)