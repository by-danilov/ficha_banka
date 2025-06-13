import os
import sys
import logging

# Добавляем корневую директорию проекта в sys.path, чтобы Python мог найти модули
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# Переименовал load_operations на load_operations_from_json для ясности
from src.utils.utils import load_operations_from_json, sort_operations_by_date
from src.file_operations.file_operations import read_operations_from_csv, read_operations_from_excel
from src.analysis.analytics import get_transactions_by_date, get_card_number_masked, get_account_number_masked
from src.analysis.additional_analytics import find_transactions_by_description
from src.analysis.additional_analytics import count_transactions_by_category

# Настройка логирования для main.py
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

log_dir = 'logs'
os.makedirs(log_dir, exist_ok=True)
file_handler = logging.FileHandler(os.path.join(log_dir, 'main.log'), mode='w', encoding='utf-8')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


def get_currency_code(transaction: dict, file_type: str) -> str:
    """
    Извлекает код валюты из транзакции в зависимости от типа исходного файла.
    """
    if file_type == 'json':
        # Для JSON-файлов валюта находится в operationAmount.currency.code
        return transaction.get('operationAmount', {}).get('currency', {}).get('code', '').upper()
    elif file_type in ['csv', 'excel']:
        # Для CSV/Excel валюта находится по ключу 'currency_code'
        return transaction.get('currency_code', '').upper()
    return ''


def format_transaction(transaction: dict, file_type: str) -> str:
    """
    Форматирует информацию о транзакции для вывода в соответствии с ТЗ.
    Принимает file_type для корректного извлечения валюты.
    """
    date = transaction.get('date', 'Дата неизвестна')
    description = transaction.get('description', 'Описание неизвестно')

    # Получаем сумму и валюту в зависимости от типа файла
    if file_type == 'json':
        amount = transaction.get('operationAmount', {}).get('amount', 'N/A')
        currency_code = transaction.get('operationAmount', {}).get('currency', {}).get('code', 'RUB')
    else:  # csv или excel
        amount = transaction.get('amount', 'N/A')
        currency_code = transaction.get('currency_code', 'RUB')  # Изменено на 'currency_code'

    from_info = transaction.get('from', '')
    to_info = transaction.get('to', '')

    # Форматирование отправителя
    formatted_from = ""
    if from_info:
        # Проверяем, является ли from_info строкой и содержит ли цифры для маскировки
        if isinstance(from_info, str) and any(char.isdigit() for char in from_info):
            # Простая эвристика: если содержит "Счет" или очень длинный набор цифр, то это счет
            if 'Счет' in from_info or len(''.join(filter(str.isdigit, from_info))) >= 10:
                formatted_from = get_account_number_masked(from_info)
            else:  # Иначе предполагаем, что это карта
                formatted_from = get_card_number_masked(from_info)
        else:  # Если from_info не строка или не содержит цифр (например, None или пустая строка)
            formatted_from = str(from_info)  # Просто преобразуем в строку

    # Форматирование получателя
    formatted_to = ""
    if to_info:
        # Проверяем, является ли to_info строкой и содержит ли цифры для маскировки
        if isinstance(to_info, str) and any(char.isdigit() for char in to_info):
            # Простая эвристика: если содержит "Счет" или очень длинный набор цифр, то это счет
            if 'Счет' in to_info or len(''.join(filter(str.isdigit, to_info))) >= 10:
                formatted_to = get_account_number_masked(to_info)
            else:  # Иначе предполагаем, что это карта
                formatted_to = get_card_number_masked(to_info)
        else:  # Если to_info не строка или не содержит цифр
            formatted_to = str(to_info)  # Просто преобразуем в строку

    output_lines = [f"{date} {description}"]
    if formatted_from and formatted_to:
        output_lines.append(f"{formatted_from} -> {formatted_to}")
    elif formatted_to:  # Если нет отправителя, но есть получатель (например, открытие вклада)
        output_lines.append(formatted_to)

    # Сумма и валюта
    output_lines.append(f"Сумма: {amount} {currency_code}")

    return "\n".join(output_lines) + "\n"


def main():
    logger.info("Запуск приложения.")
    # Путь к папке data, которая находится на том же уровне, что и src
    data_dir = os.path.join(project_root, 'data')

    json_path = os.path.join(data_dir, 'operations.json')
    csv_path = os.path.join(data_dir, 'transactions.csv')
    excel_path = os.path.join(data_dir, 'transactions_excel.xlsx')

    operations = []
    selected_file_type = ""  # Переменная для хранения типа выбранного файла

    print("Привет! Добро пожаловать в программу работы с банковскими транзакциями.")

    while True:
        print("\nВыберите необходимый пункт меню:")
        print("1. Получить информацию о транзакциях из JSON-файла")
        print("2. Получить информацию о транзакциях из CSV-файла")
        print("3. Получить информацию о транзакциях из XLSX-файла")
        print("0. Выход")

        file_choice = input("Ваш выбор: ")

        if file_choice == '1':
            logger.info("Пользователь выбрал JSON-файл.")
            print("Для обработки выбран JSON-файл.")
            operations = load_operations_from_json(json_path)  # Используем load_operations_from_json
            selected_file_type = 'json'
            break
        elif file_choice == '2':
            logger.info("Пользователь выбрал CSV-файл.")
            print("Для обработки выбран CSV-файл.")
            operations = read_operations_from_csv(csv_path)
            selected_file_type = 'csv'
            break
        elif file_choice == '3':
            logger.info("Пользователь выбрал XLSX-файл.")
            print("Для обработки выбран XLSX-файл.")
            operations = read_operations_from_excel(excel_path)
            selected_file_type = 'excel'
            break
        elif file_choice == '0':
            logger.info("Пользователь выбрал выход из программы.")
            print("До свидания!")
            return
        else:
            print("Некорректный выбор. Пожалуйста, попробуйте еще раз.")
            logger.warning(f"Некорректный выбор файла: {file_choice}")

    if not operations:
        logger.error("Не удалось загрузить операции из выбранного файла. Проверьте его наличие и формат.")
        print("Не удалось загрузить операции из выбранного файла. Проверьте его наличие и формат.")
        return

    filtered_operations = list(operations)  # Копируем список для дальнейшей фильтрации

    # --- Фильтрация по статусу ---
    # Для CSV/Excel статус теперь 'state', для JSON - 'state'.
    # В file_operations мы привели 'state' к верхнему регистру, поэтому здесь просто используем 'state'
    available_statuses = {"EXECUTED", "CANCELED", "PENDING"}
    while True:
        print("\nВведите статус, по которому необходимо выполнить фильтрацию.")
        print(f"Доступные для фильтровки статусы: {', '.join(available_statuses)}")
        status_input = input("Ваш статус: ").upper().strip()

        if status_input in available_statuses:
            # Для JSON статус 'state', для CSV/Excel тоже 'state' после обработки в file_operations
            filtered_operations = [op for op in filtered_operations if op.get('state', '').upper() == status_input]
            print(f"Операции отфильтрованы по статусу \"{status_input}\"")
            logger.info(
                f"Операции отфильтрованы по статусу: {status_input}. Осталось {len(filtered_operations)} операций.")
            break
        else:
            print(f"Статус операции \"{status_input}\" недоступен.")
            logger.warning(f"Пользователь ввел недопустимый статус: {status_input}")

    # Если после фильтрации по статусу список пуст, можем сразу выйти
    if not filtered_operations:
        print("\nНе найдено ни одной транзакции, подходящей под ваши условия фильтрации.")
        logger.info("Выборка пуста после фильтрации по статусу.")
        return

    # --- Сортировка по дате ---
    sort_by_date_choice = input("Отсортировать операции по дате? Да/Нет: ").lower().strip()
    if sort_by_date_choice == 'да':
        while True:
            sort_order_choice = input(
                "Отсортировать по возрастанию или по убыванию? (по возрастанию/по убыванию): ").lower().strip()
            if sort_order_choice == 'по возрастанию':
                filtered_operations = sort_operations_by_date(filtered_operations, reverse=False)
                logger.info("Операции отсортированы по возрастанию даты.")
                break
            elif sort_order_choice == 'по убыванию':
                filtered_operations = sort_operations_by_date(filtered_operations, reverse=True)
                logger.info("Операции отсортированы по убыванию даты.")
                break
            else:
                print("Некорректный выбор. Пожалуйста, введите 'по возрастанию' или 'по убыванию'.")
                logger.warning(f"Некорректный выбор порядка сортировки: {sort_order_choice}")
    else:
        logger.info("Пользователь отказался от сортировки по дате.")

    # --- Фильтрация по рублям (исправлено с учетом типа файла) ---
    filter_rub_choice = input("Выводить только рублевые транзакции? Да/Нет: ").lower().strip()
    if filter_rub_choice == 'да':
        filtered_operations = [op for op in filtered_operations if get_currency_code(op, selected_file_type) == 'RUB']
        logger.info(f"Операции отфильтрованы по валюте (только RUB). Осталось {len(filtered_operations)} операций.")
    else:
        logger.info("Пользователь отказался от фильтрации по рублям.")

    # --- Фильтрация по слову в описании ---
    filter_description_choice = input(
        "Отфильтровать список транзакций по определенному слову в описании? Да/Нет: ").lower().strip()
    if filter_description_choice == 'да':
        search_word = input("Введите слово для поиска в описании: ").strip()
        if search_word:
            filtered_operations = find_transactions_by_description(filtered_operations, search_word)
            logger.info(
                f"Операции отфильтрованы по слову в описании: '{search_word}'. Осталось {len(filtered_operations)} операций.")
        else:
            print("Слово для поиска не введено. Фильтрация по описанию не выполнена.")
            logger.warning("Пустое слово для поиска описания.")
    else:
        logger.info("Пользователь отказался от фильтрации по описанию.")

    print("\nРаспечатываю итоговый список транзакций...\n")

    if not filtered_operations:
        print("Не найдено ни одной транзакции, подходящей под ваши условия фильтрации")
        logger.info("Итоговая выборка пуста.")
    else:
        print(f"Всего банковских операций в выборке: {len(filtered_operations)}\n")
        for op in filtered_operations:
            print(format_transaction(op, selected_file_type))
            print("-" * 30)
        logger.info(f"Отображено {len(filtered_operations)} итоговых транзакций.")

    logger.info("Завершение работы приложения.")


if __name__ == '__main__':
    main()
