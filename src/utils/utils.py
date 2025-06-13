# src/utils/utils.py
import json
import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

log_dir = 'logs'
os.makedirs(log_dir, exist_ok=True)
file_handler = logging.FileHandler(os.path.join(log_dir, 'utils.log'), mode='w', encoding='utf-8')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


def load_operations_from_json(json_filepath: str) -> list[dict]:
    """
    Загружает список финансовых операций из JSON файла.
    Возвращает пустой список, если файл не найден, пуст или содержит некорректные данные.
    """
    if not os.path.exists(json_filepath):
        logger.error(f"JSON файл не найден: {json_filepath}")
        return []

    try:
        with open(json_filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if not isinstance(data, list):
                logger.error(f"JSON файл {json_filepath} содержит некорректный формат данных (ожидается список).")
                return []
            # Фильтруем пустые или некорректные записи
            operations = [op for op in data if isinstance(op, dict) and op.get('id') is not None]
            logger.info(f"Успешно загружено {len(operations)} операций из JSON файла: {json_filepath}")
            return operations
    except json.JSONDecodeError as e:
        logger.error(f"Ошибка декодирования JSON файла {json_filepath}: {e}")
        return []
    except Exception as e:
        logger.error(f"Неожиданная ошибка при чтении JSON файла {json_filepath}: {e}")
        return []

def sort_operations_by_date(operations: list[dict], reverse: bool = False) -> list[dict]:
    """
    Сортирует список финансовых операций по дате.
    Дата может быть в формате 'YYYY-MM-DDTHH:MM:SSZ' или 'DD.MM.YYYY'.
    """
    # Дополнительная функция для парсинга даты
    def parse_date(date_str: str) -> datetime:
        try:
            # Попытка парсинга ISO формата (JSON)
            return datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%SZ')
        except ValueError:
            try:
                # Попытка парсинга DD.MM.YYYY (старый CSV)
                return datetime.strptime(date_str, '%d.%m.%Y')
            except ValueError:
                # В случае новой структуры CSV/Excel, дата может быть в формате 'YYYY-MM-DDTHH:MM:SSZ'
                # или просто 'YYYY-MM-DD'. Добавим еще одну попытку.
                try:
                    return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                except ValueError:
                    logger.warning(f"Не удалось распознать формат даты: {date_str}. Возвращаю минимальную дату.")
                    return datetime.min # Возвращаем минимальную дату для некорректных дат

    try:
        # Убедимся, что операции имеют ключ 'date' перед сортировкой
        valid_operations = [op for op in operations if 'date' in op and op['date']]
        sorted_ops = sorted(valid_operations, key=lambda x: parse_date(x['date']), reverse=reverse)
        logger.info(f"Операции отсортированы по дате (обратный порядок: {reverse}).")
        return sorted_ops
    except Exception as e:
        logger.error(f"Ошибка при сортировке операций по дате: {e}")
        return list(operations) # Возвращаем копию исходного списка в случае ошибки