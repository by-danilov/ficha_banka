import csv
import logging
import os

import openpyxl

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

log_dir = 'logs'
os.makedirs(log_dir, exist_ok=True)
file_handler = logging.FileHandler(os.path.join(log_dir, 'file_operations.log'), mode='w')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


def read_operations_from_csv(csv_filepath: str) -> list[dict]:
    """
    Считывает финансовые операции из CSV-файла.

    Args:
        csv_filepath (str): Путь к CSV-файлу.

    Returns:
        list[dict]: Список словарей, представляющих транзакции.
                     Возвращает пустой список в случае ошибки.
    """
    operations = []
    try:
        with open(csv_filepath, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            if reader.fieldnames:
                logger.info(f"Начато чтение CSV файла: '{csv_filepath}'. Заголовки: {reader.fieldnames}")
                for row in reader:
                    operations.append(row)
                logger.info(f"Успешно прочитано {len(operations)} операций из CSV файла: '{csv_filepath}'.")
            else:
                logger.warning(f"CSV файл '{csv_filepath}' пуст или не содержит заголовков.")
    except FileNotFoundError:
        logger.error(f"CSV файл не найден: '{csv_filepath}'.")
    except Exception as e:
        logger.error(f"Произошла ошибка при чтении CSV файла '{csv_filepath}': {e}")
    return operations


def read_operations_from_excel(excel_filepath: str) -> list[dict]:
    """
    Считывает финансовые операции из XLSX-файла.

    Args:
        excel_filepath (str): Путь к XLSX-файлу.

    Returns:
        list[dict]: Список словарей, представляющих транзакции.
                     Возвращает пустой список в случае ошибки.
    """
    operations = []
    try:
        workbook = openpyxl.load_workbook(excel_filepath)
        sheet = workbook.active
        header_row = [cell.value for cell in sheet[1]]
        # Проверяем, что первая строка содержит хотя бы одно непустое значение (заголовок)
        if any(header_row):
            header = header_row
            logger.info(f"Начато чтение Excel файла: '{excel_filepath}'. Заголовки: {header}")
            for row_index in range(2, sheet.max_row + 1):
                row_data = [cell.value for cell in sheet[row_index]]
                operation = dict(zip(header, row_data))
                operations.append(operation)
            logger.info(f"Успешно прочитано {len(operations)} операций из Excel файла: '{excel_filepath}'.")
        else:
            logger.warning(f"Excel файл '{excel_filepath}' пуст или не содержит заголовков на первой строке.")
            return []
    except FileNotFoundError:
        logger.error(f"Excel файл не найден: '{excel_filepath}'.")
    except Exception as e:
        logger.error(f"Произошла ошибка при чтении Excel файла '{excel_filepath}': {e}")
    return operations
