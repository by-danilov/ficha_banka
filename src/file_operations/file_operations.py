# src/file_operations/file_operations.py
import csv
import logging
import os
import openpyxl
from datetime import datetime

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

log_dir = 'logs'
os.makedirs(log_dir, exist_ok=True)
file_handler = logging.FileHandler(os.path.join(log_dir, 'file_operations.log'), mode='w', encoding='utf-8')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


def read_operations_from_csv(csv_filepath: str) -> list[dict]:
    """
    Считывает финансовые операции из CSV-файла с валидацией и приведением типов,
    учитывая структуру колонок из скриншота.

    Args:
        csv_filepath (str): Путь к CSV-файлу.

    Returns:
        list[dict]: Список словарей, представляющих транзакции.
                     Возвращает пустой список в случае ошибки.
    """
    operations = []
    if not os.path.exists(csv_filepath):
        logger.error(f"CSV файл не найден: '{csv_filepath}'.")
        return []
    try:
        with open(csv_filepath, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            required_headers = ['id', 'state', 'date', 'amount', 'currency_name', 'description']

            if not all(header in reader.fieldnames for header in required_headers):
                missing_headers = [header for header in required_headers if header not in reader.fieldnames]
                logger.error(
                    f"CSV файл '{csv_filepath}' не содержит всех обязательных заголовков: {missing_headers}. Найдено: {reader.fieldnames}")
                return []

            logger.info(f"Начато чтение CSV файла: '{csv_filepath}'. Заголовки: {reader.fieldnames}")
            for i, row in enumerate(reader):
                try:
                    operation = {
                        'id': int(row['id']),
                        'description': str(row['description']),
                        'amount': float(row['amount']),
                        'currency': str(row['currency_name']),
                        'date': str(row['date']),
                        'status': str(row['state']),
                        'from': str(row.get('from', '')),
                        'to': str(row.get('to', ''))
                    }
                    operations.append(operation)
                except (ValueError, KeyError, TypeError) as e:
                    logger.warning(
                        f"Пропущена строка {i + 2} (с учетом заголовка) из CSV файла '{csv_filepath}' из-за некорректных данных: {row}. Ошибка: {e}")
            logger.info(f"Успешно прочитано {len(operations)} операций из CSV файла: '{csv_filepath}'.")
    except Exception as e:
        logger.error(f"Произошла ошибка при чтении CSV файла '{csv_filepath}': {e}")
    return operations


def read_operations_from_excel(excel_filepath: str) -> list[dict]:
    """
    Считывает финансовые операции из XLSX-файла с валидацией и приведением типов,
    учитывая структуру колонок из скриншота.

    Args:
        excel_filepath (str): Путь к XLSX-файлу.

    Returns:
        list[dict]: Список словарей, представляющих транзакции.
                     Возвращает пустой список в случае ошибки.
    """
    operations = []
    if not os.path.exists(excel_filepath):
        logger.error(f"Excel файл не найден: '{excel_filepath}'.")
        return []
    try:
        workbook = openpyxl.load_workbook(excel_filepath)
        sheet = workbook.active

        header_row = [cell.value for cell in sheet[1]]

        required_headers = ['id', 'state', 'date', 'amount', 'currency_name', 'description']

        if not all(header in header_row for header in required_headers):
            missing_headers = [header for header in required_headers if header not in header_row]
            logger.error(
                f"Excel файл '{excel_filepath}' не содержит всех обязательных заголовков: {missing_headers}. Найдено: {header_row}")
            return []

        if any(header_row):
            header = header_row
            logger.info(f"Начато чтение Excel файла: '{excel_filepath}'. Заголовки: {header}")
            for row_index in range(2, sheet.max_row + 1):
                row_data = {}
                for col_index, h in enumerate(header):
                    cell_value = sheet.cell(row=row_index, column=col_index + 1).value
                    row_data[h] = cell_value

                try:
                    date_value = row_data.get('date')
                    if isinstance(date_value, datetime):
                        date_str = date_value.strftime('%d.%m.%Y')
                    else:
                        date_str = str(date_value) if date_value is not None else ''

                    operation = {
                        'id': int(row_data['id']),
                        'description': str(row_data['description']),
                        'amount': float(row_data['amount']),
                        'currency': str(row_data['currency_name']),
                        'date': date_str,
                        'status': str(row_data['state']),
                        'from': str(row_data.get('from', '')),
                        'to': str(row_data.get('to', ''))
                    }
                    operations.append(operation)
                except (ValueError, KeyError, TypeError) as e:
                    logger.warning(
                        f"Пропущена строка {row_index} из Excel файла '{excel_filepath}' из-за некорректных данных: {row_data}. Ошибка: {e}")
            logger.info(f"Успешно прочитано {len(operations)} операций из Excel файла: '{excel_filepath}'.")
        else:
            logger.warning(f"Excel файл '{excel_filepath}' пуст или не содержит заголовков на первой строке.")
            return []
    except FileNotFoundError:
        logger.error(f"Excel файл не найден: '{excel_filepath}'.")
    except Exception as e:
        logger.error(f"Произошла ошибка при чтении Excel файла '{excel_filepath}': {e}")
    return operations


if __name__ == '__main__':
    current_dir = os.path.dirname(os.path.abspath(__file__))

    csv_path = os.path.join(current_dir, '..', '..', 'data', 'transactions.csv')
    print(f"Попытка загрузки CSV из: {csv_path}")
    csv_ops = read_operations_from_csv(csv_path)
    if csv_ops:
        print(f"Загружено {len(csv_ops)} CSV операций. Первая: {csv_ops[0]}")
    else:
        print("Не удалось загрузить CSV операции.")

    excel_path = os.path.join(current_dir, '..', '..', 'data', 'transactions_excel.xlsx')
    print(f"\nПопытка загрузки Excel из: {excel_path}")
    excel_ops = read_operations_from_excel(excel_path)
    if excel_ops:
        print(f"Загружено {len(excel_ops)} Excel операций. Первая: {excel_ops[0]}")
    else:
        print("Не удалось загрузить Excel операции.")
