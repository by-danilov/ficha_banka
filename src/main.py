# src/main.py
import os
import sys
import logging
import re  # Для маскирования карт/счетов
from datetime import datetime  # Для сортировки по дате

# Импортируем загрузчики. Пока есть только CSV. JSON и XLSX потребуют создания своих загрузчиков.
from src.data.transaction_loader import load_transactions_from_csv
# from src.data.json_loader import load_transactions_from_json # Если будет
# from src.data.xlsx_loader import load_transactions_from_xlsx # Если будет

from src.analysis.transaction_analyzer import find_transactions_by_description, count_transactions_by_category

# Настройка логгера для модуля main
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

log_dir = 'logs'
os.makedirs(log_dir, exist_ok=True)
file_handler = logging.FileHandler(os.path.join(log_dir, 'main.log'), mode='w', encoding='utf-8')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Допустимые статусы операций
ALLOWED_STATUSES = ['EXECUTED', 'CANCELED', 'PENDING']


def mask_card_number(card_info: str) -> str:
    """Маскирует номер карты или счета в строке, оставляя первые 6 и последние 4 цифры открытыми."""
    if not card_info:
        return "N/A"

    # Поиск последовательности цифр, похожей на номер карты/счета
    # Ищем 16 цифр (карты) или 4-20 цифр (счета), или даже просто счет **XXXX
    match = re.search(r'(\d{4}\s?\d{2})\d{6,8}(\d{4})', card_info)  # Для MasterCard 7771 27** **** 3727
    if match:
        # Для карт: первые 6, последние 4, остальное звездочки
        masked_part = f"{match.group(1)}** **** {match.group(2)}"
        return card_info.replace(match.group(0), masked_part)

    match_account = re.search(r'(\d{4,})(\d{4})$', card_info)  # Для Счета **4321
    if match_account and len(match_account.group(1)) > 4:  # Если есть больше 4 цифр в начале
        # Счета: маскируем все, кроме последних 4 цифр
        masked_part = f"Счет **{match_account.group(2)}"
        return card_info.replace(match_account.group(0), masked_part)

    # Если это просто "Счет XXXX" или "Visa Platinum" без полного номера,
    # или не удалось найти паттерн, возвращаем исходное или немного модифицированное
    if 'Счет' in card_info and len(card_info.split()[-1]) > 4 and card_info.split()[-1].isdigit():
        return f"Счет **{card_info.split()[-1][-4:]}"

    # Если это просто название карты без полного номера, оставляем как есть
    if 'MasterCard' in card_info or 'Visa' in card_info:
        return card_info

    return card_info  # Возвращаем исходное, если не удалось замаскировать


def format_transaction_output(transaction: dict) -> str:
    """
    Форматирует информацию о транзакции для вывода в консоль.
    Маскирует номера карт/счетов.
    """
    date_str = transaction.get('date', 'N/A')
    description = transaction.get('description', 'N/A')
    amount = transaction.get('amount', 'N/A')
    currency = transaction.get('currency', 'N/A')
    _from = transaction.get('from', '')
    _to = transaction.get('to', '')

    # Маскирование номеров
    masked_from = mask_card_number(_from)
    masked_to = mask_card_number(_to)

    output = f"{date_str} {description}\n"
    if masked_from and masked_to:
        output += f"{masked_from} -> {masked_to}\n"
    elif masked_from:
        output += f"{masked_from}\n"
    elif masked_to:
        output += f"{masked_to}\n"

    output += f"Сумма: {amount} {currency}\n"
    return output


def main():
    """
    Главная функция программы для анализа банковских операций.
    Загружает данные, предоставляет меню выбора действий пользователю
    и выводит результаты анализа.
    """
    logger.info("Приложение запущено.")
    transactions = []

    # Приветственное сообщение
    print("\n" + "=" * 70)
    print("        Привет! Добро пожаловать в программу работы")
    print("        с банковскими транзакциями.")
    print("=" * 70)

    # Шаг 1: Выбор источника данных
    while True:
        print("\nВыберите необходимый пункт меню:")
        print("1. Получить информацию о транзакциях из JSON-файла (пока не реализовано)")
        print("2. Получить информацию о транзакциях из CSV-файла")
        print("3. Получить информацию о транзакциях из XLSX-файла (пока не реализовано)")
        file_choice = input("Ваш выбор: ").strip()

        file_path = ""
        if file_choice == '1':
            print("Для обработки выбран JSON-файл. (Функционал загрузки JSON пока не реализован).")
            logger.warning("Пользователь выбрал JSON, но загрузчик не реализован.")
            # Здесь в будущем будет вызов load_transactions_from_json
            # file_path = os.path.join('data', 'operations.json') # Пример пути
            # transactions = load_transactions_from_json(file_path)
            continue  # Пока что продолжаем цикл до выбора реализованной опции
        elif file_choice == '2':
            print("Для обработки выбран CSV-файл.")
            file_path = os.path.join('data', 'transactions.csv')
            if not os.path.exists(file_path):
                logger.error(f"Файл данных не найден: {file_path}. Убедитесь, что он находится в папке 'data'.")
                print(f"Ошибка: Файл '{file_path}' не найден. Пожалуйста, убедитесь, что он находится в папке 'data'.")
                sys.exit(1)
            transactions = load_transactions_from_csv(file_path)
            if not transactions:
                logger.warning("Не удалось загрузить транзакции или файл пуст.")
                print("Не удалось загрузить транзакции или файл данных пуст. Завершение работы.")
                sys.exit(0)
            break
        elif file_choice == '3':
            print("Для обработки выбран XLSX-файл. (Функционал загрузки XLSX пока не реализован).")
            logger.warning("Пользователь выбрал XLSX, но загрузчик не реализован.")
            # Здесь в будущем будет вызов load_transactions_from_xlsx
            continue  # Пока что продолжаем цикл до выбора реализованной опции
        else:
            print("Некорректный выбор. Пожалуйста, введите 1, 2 или 3.")
            logger.warning(f"Пользователь ввел некорректный выбор источника: '{file_choice}'.")

    # Шаг 2: Фильтрация по статусу
    filtered_transactions = transactions[:]  # Начинаем с копии всех загруженных транзакций

    while True:
        print("\nВведите статус, по которому необходимо выполнить фильтрацию.")
        print(f"Доступные для фильтровки статусы: {', '.join(ALLOWED_STATUSES)}")
        status_input = input("Пользователь: ").strip().upper()  # Приводим к верхнему регистру для сравнения

        if status_input in ALLOWED_STATUSES:
            selected_status = status_input
            print(f"Операции отфильтрованы по статусу \"{selected_status}\"")
            logger.info(f"Операции отфильтрованы по статусу: '{selected_status}'.")

            # Применяем фильтрацию по статусу
            filtered_transactions = [
                tx for tx in filtered_transactions if tx.get('status', '').upper() == selected_status
            ]
            break
        else:
            print(f"Статус операции \"{status_input}\" недоступен.")
            logger.warning(f"Пользователь ввел неверный статус: '{status_input}'.")

    # Шаг 3: Сортировка по дате
    while True:
        sort_by_date_choice = input("\nОтсортировать операции по дате? Да/Нет: ").strip().lower()
        if sort_by_date_choice in ['да', 'нет']:
            break
        else:
            print("Некорректный ввод. Пожалуйста, введите 'Да' или 'Нет'.")
            logger.warning(f"Пользователь ввел некорректный ответ на сортировку по дате: '{sort_by_date_choice}'.")

    if sort_by_date_choice == 'да':
        while True:
            sort_order_choice = input("Отсортировать по возрастанию или по убыванию? ").strip().lower()
            if sort_order_choice in ['по возрастанию', 'по убыванию']:
                break
            else:
                print("Некорректный ввод. Пожалуйста, введите 'по возрастанию' или 'по убыванию'.")
                logger.warning(f"Пользователь ввел некорректный ответ на порядок сортировки: '{sort_order_choice}'.")

        try:
            # Для сортировки по дате: конвертируем строку в объект datetime
            filtered_transactions.sort(
                key=lambda x: datetime.strptime(x.get('date', '01.01.1900'), '%d.%m.%Y'),
                reverse=(sort_order_choice == 'по убыванию')
            )
            logger.info(f"Транзакции отсортированы по дате: {sort_order_choice}.")
        except Exception as e:
            logger.error(f"Ошибка при сортировке по дате: {e}")
            print("Не удалось отсортировать операции по дате.")

    # Шаг 4: Фильтрация по рублевым транзакциям
    while True:
        filter_rub_choice = input("\nВыводить только рублевые транзакции? Да/Нет: ").strip().lower()
        if filter_rub_choice in ['да', 'нет']:
            break
        else:
            print("Некорректный ввод. Пожалуйста, введите 'Да' или 'Нет'.")
            logger.warning(f"Пользователь ввел некорректный ответ на фильтрацию по рублям: '{filter_rub_choice}'.")

    if filter_rub_choice == 'да':
        filtered_transactions = [
            tx for tx in filtered_transactions if tx.get('currency', '').upper() == 'RUB'
        ]
        logger.info("Отфильтрованы только рублевые транзакции.")

    # Шаг 5: Фильтрация по слову в описании
    while True:
        filter_description_choice = input(
            "\nОтфильтровать список транзакций по определенному слову в описании? Да/Нет: ").strip().lower()
        if filter_description_choice in ['да', 'нет']:
            break
        else:
            print("Некорректный ввод. Пожалуйста, введите 'Да' или 'Нет'.")
            logger.warning(
                f"Пользователь ввел некорректный ответ на фильтрацию по описанию: '{filter_description_choice}'.")

    if filter_description_choice == 'да':
        search_word = input("Введите слово для фильтрации по описанию: ").strip()
        # Используем существующую функцию find_transactions_by_description
        # Она уже использует re.IGNORECASE, что хорошо
        filtered_transactions = find_transactions_by_description(filtered_transactions, search_word)
        logger.info(f"Отфильтрованы транзакции по слову в описании: '{search_word}'.")

    # Шаг 6: Вывод результатов
    print("\nРаспечатываю итоговый список транзакций...")

    if not filtered_transactions:
        print("\nНе найдено ни одной транзакции, подходящей под ваши условия фильтрации.")
        logger.info("Итоговая выборка транзакций пуста.")
    else:
        print(f"\nВсего банковских операций в выборке: {len(filtered_transactions)}\n")
        for tx in filtered_transactions:
            print(format_transaction_output(tx))
            print("-" * 30)  # Разделитель между транзакциями
        logger.info(f"Выведено {len(filtered_transactions)} транзакций.")

    print("\nСпасибо за использование программы! До свидания.")
    logger.info("Приложение завершено.")
    sys.exit(0)  # Завершаем программу после вывода результатов


if __name__ == '__main__':
    main()