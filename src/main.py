# src/main.py
import os
import sys
import logging
from src.data.transaction_loader import load_transactions_from_csv
from src.analysis.transaction_analyzer import find_transactions_by_description, count_transactions_by_category

# Настройка логгера для модуля main
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)  # Установим уровень INFO для консоли/файла по умолчанию

# Убедимся, что папка logs существует
log_dir = 'logs'
os.makedirs(log_dir, exist_ok=True)

# Настройка файлового обработчика для записи логов в файл
file_handler = logging.FileHandler(os.path.join(log_dir, 'main.log'), mode='w', encoding='utf-8')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Пример списка допустимых статусов (вы можете изменить его под свои нужды)
# Если в transactions.csv есть колонка 'status', используйте ее значения.
ALLOWED_STATUSES = ['успешно', 'отменено', 'ожидает']


def main():
    """
    Главная функция программы для анализа банковских операций.
    Загружает данные, предоставляет меню выбора действий пользователю
    и выводит результаты анализа.
    """
    logger.info("Приложение запущено.")
    # Путь к файлу transactions.csv, который находится в корневой папке data
    csv_file_path = os.path.join('data', 'transactions.csv')

    # Проверяем наличие файла CSV
    if not os.path.exists(csv_file_path):
        logger.error(f"Файл данных не найден: {csv_file_path}. Убедитесь, что файл находится в папке 'data'.")
        print(f"Ошибка: Файл '{csv_file_path}' не найден. Пожалуйста, убедитесь, что он находится в папке 'data'.")
        sys.exit(1)

    transactions = load_transactions_from_csv(csv_file_path)

    if not transactions:
        logger.warning("Не удалось загрузить транзакции или файл пуст.")
        print("Не удалось загрузить транзакции или файл данных пуст. Завершение работы.")
        sys.exit(0)

    # Приветственное сообщение
    print("\n" + "=" * 60)
    print("        Добро пожаловать в анализатор банковских операций!")
    print("=" * 60)

    # Переменная для хранения выбранного статуса
    selected_status = None

    while True:
        print("\n" + "-" * 60)
        print("  Текущий выбранный статус: " + (selected_status.capitalize() if selected_status else "Не выбран"))
        print("-" * 60)
        print("\nВыберите действие:")
        print("0. Выбрать/сбросить статус операции")
        print("1. Найти операции по описанию")
        print("2. Подсчитать операции по категориям")
        print("3. Выход")

        choice = input("Ваш выбор: ").strip()

        if choice == '0':  # Логика для выбора статуса
            print("\nДоступные статусы:")
            for i, status in enumerate(ALLOWED_STATUSES):
                print(f"{i + 1}. {status.capitalize()}")
            print(f"0. Отмена выбора статуса (сбросить текущий статус)")

            while True:
                status_choice = input(
                    f"Введите номер статуса (1-{len(ALLOWED_STATUSES)}) или 0 для отмены/сброса: ").strip()
                if status_choice == '0':
                    selected_status = None
                    print("Выбор статуса отменен. Операции будут обрабатываться без фильтрации по статусу.")
                    logger.info("Пользователь отменил выбор статуса.")
                    break
                try:
                    status_index = int(status_choice) - 1
                    if 0 <= status_index < len(ALLOWED_STATUSES):
                        selected_status = ALLOWED_STATUSES[status_index]
                        print(f"Статус операции установлен на: {selected_status.capitalize()}")
                        logger.info(f"Статус операции установлен на: '{selected_status}'.")
                        break
                    else:
                        print("Неверный номер статуса. Пожалуйста, введите номер из списка.")
                        logger.warning(f"Пользователь ввел неверный номер статуса: '{status_choice}'.")
                except ValueError:
                    print("Некорректный ввод. Пожалуйста, введите числовой номер статуса.")
                    logger.warning(f"Пользователь ввел некорректный символ для выбора статуса: '{status_choice}'.")


        elif choice == '1':
            search_query = input("Введите строку для поиска в описании (можно использовать рег. выражения): ").strip()

            # Если в будущем понадобится фильтрация по статусу:
            # filtered_by_status_transactions = [tx for tx in transactions if selected_status is None or tx.get('status') == selected_status]
            # found_transactions = find_transactions_by_description(filtered_by_status_transactions, search_query)

            found_transactions = find_transactions_by_description(transactions, search_query)

            if found_transactions:
                print("\nНайденные транзакции:")
                for tx in found_transactions:
                    print(f"ID: {tx.get('id', 'N/A')}, "
                          f"Описание: {tx.get('description', 'N/A')}, "
                          f"Сумма: {tx.get('amount', 'N/A')}, "
                          f"Валюта: {tx.get('currency', 'N/A')}")
            else:
                print("Транзакции, соответствующие вашему запросу, не найдены.")
            logger.info(
                f"Пользователь выполнил поиск по описанию: '{search_query}'. Найдено: {len(found_transactions)}. (Выбран статус: {selected_status})")

        elif choice == '2':
            categories_input = input("Введите категории через запятую (например: Перевод, Покупка, Услуги): ").strip()
            categories = [cat.strip() for cat in categories_input.split(',') if cat.strip()]

            if not categories:
                print("Вы не ввели ни одной категории. Пожалуйста, попробуйте еще раз.")
                logger.warning("Пользователь попытался подсчитать категории, но не ввел ни одной.")
                continue

            # Если в будущем понадобится фильтрация по статусу:
            # filtered_by_status_transactions = [tx for tx in transactions if selected_status is None or tx.get('status') == selected_status]
            # category_counts = count_transactions_by_category(filtered_by_status_transactions, categories)

            category_counts = count_transactions_by_category(transactions, categories)
            if category_counts:
                print("\nПодсчет операций по категориям:")
                for category, count in category_counts.items():
                    print(f"- {category}: {count}")
            else:
                print("Не удалось подсчитать операции по категориям или список категорий пуст.")
            logger.info(
                f"Пользователь выполнил подсчет по категориям: {categories}. Результат: {category_counts}. (Выбран статус: {selected_status})")

        elif choice == '3':
            print("Спасибо за использование программы! До свидания.")
            logger.info("Приложение завершено пользователем.")
            break
        else:
            print("Некорректный выбор. Пожалуйста, введите 0, 1, 2 или 3.")
            logger.warning(f"Пользователь ввел некорректный выбор меню: '{choice}'.")
