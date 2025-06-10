# src/main.py
import os
import sys
import logging
from src.data.transaction_loader import load_transactions_from_csv
from src.analysis.transaction_analyzer import find_transactions_by_description, count_transactions_by_category

# Настройка логгера для модуля main
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

log_dir = 'logs'
os.makedirs(log_dir, exist_ok=True)
file_handler = logging.FileHandler(os.path.join(log_dir, 'main.log'), mode='w')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


def main():
    """
    Главная функция программы для анализа банковских операций.
    Загружает данные, предоставляет меню выбора действий пользователю
    и выводит результаты анализа.
    """
    logger.info("Приложение запущено.")
    csv_file_path = os.path.join('data', 'transactions.csv')

    # Проверяем наличие файла CSV
    if not os.path.exists(csv_file_path):
        logger.error(f"Файл данных не найден: {csv_file_path}. Убедитесь, что файл существует.")
        print(f"Ошибка: Файл '{csv_file_path}' не найден. Пожалуйста, убедитесь, что он находится в папке 'data'.")
        sys.exit(1)

    transactions = load_transactions_from_csv(csv_file_path)

    if not transactions:
        logger.warning("Не удалось загрузить транзакции или файл пуст.")
        print("Не удалось загрузить транзакции или файл данных пуст. Завершение работы.")
        sys.exit(0)

    print("\nДобро пожаловать в анализатор банковских операций!")

    while True:
        print("\nВыберите действие:")
        print("1. Найти операции по описанию")
        print("2. Подсчитать операции по категориям")
        print("3. Выход")

        choice = input("Ваш выбор: ").strip()

        if choice == '1':
            search_query = input("Введите строку для поиска в описании (можно использовать рег. выражения): ").strip()
            found_transactions = find_transactions_by_description(transactions, search_query)
            if found_transactions:
                print("\nНайденные транзакции:")
                for tx in found_transactions:
                    # Убедимся, что все ключи, которые мы ожидаем выводить, существуют
                    # или используем .get() с дефолтным значением
                    print(f"ID: {tx.get('id', 'N/A')}, "
                          f"Описание: {tx.get('description', 'N/A')}, "
                          f"Сумма: {tx.get('amount', 'N/A')}")
            else:
                print("Транзакции, соответствующие вашему запросу, не найдены.")
            logger.info(
                f"Пользователь выполнил поиск по описанию: '{search_query}'. Найдено: {len(found_transactions)}.")

        elif choice == '2':
            categories_input = input("Введите категории через запятую (например: Перевод, Покупка, Услуги): ").strip()
            categories = [cat.strip() for cat in categories_input.split(',') if cat.strip()]

            if not categories:
                print("Вы не ввели ни одной категории. Пожалуйста, попробуйте еще раз.")
                logger.warning("Пользователь попытался подсчитать категории, но не ввел ни одной.")
                continue

            category_counts = count_transactions_by_category(transactions, categories)
            if category_counts:
                print("\nПодсчет операций по категориям:")
                for category, count in category_counts.items():
                    print(f"- {category}: {count}")
            else:
                print("Не удалось подсчитать операции по категориям или список категорий пуст.")
            logger.info(f"Пользователь выполнил подсчет по категориям: {categories}. Результат: {category_counts}.")

        elif choice == '3':
            print("Спасибо за использование программы! До свидания.")
            logger.info("Приложение завершено пользователем.")
            break
        else:
            print("Некорректный выбор. Пожалуйста, введите 1, 2 или 3.")
            logger.warning(f"Пользователь ввел некорректный выбор меню: '{choice}'.")
