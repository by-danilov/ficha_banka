import logging
import json
import os

# Создаем логгер для модуля utils
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Создаем обработчик для записи логов в файл
log_dir = 'logs'
os.makedirs(log_dir, exist_ok=True)
file_handler = logging.FileHandler(os.path.join(log_dir, 'utils.log'), mode='w')

# Создаем форматтер
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Добавляем обработчик к логгеру
logger.addHandler(file_handler)

def load_operations(file_path):
    """Загружает операции из JSON файла."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            logger.info(f"Успешно загружены операции из файла: '{file_path}'")
            return data
    except FileNotFoundError:
        logger.error(f"Файл не найден: '{file_path}'")
        return None
    except json.JSONDecodeError:
        logger.error(f"Ошибка декодирования JSON в файле: '{file_path}'")
        return None

def sort_operations_by_date(operations, reverse=False):
    """Сортирует список операций по дате."""
    if not isinstance(operations, list):
        logger.warning("Передан некорректный тип данных для сортировки операций.")
        return operations
    try:
        sorted_ops = sorted(operations, key=lambda x: x.get('date', ''), reverse=reverse)
        logger.debug(f"Операции отсортированы по дате (reverse={reverse}). Количество операций: {len(sorted_ops)}")
        return sorted_ops
    except Exception as e:
        logger.error(f"Ошибка при сортировке операций: {e}")
        return operations

if __name__ == '__main__':
    # Пример использования
    operations_file = 'data/operations.json'
    operations = load_operations(operations_file)
    if operations:
        print(f"Загружено {len(operations)} операций.")
        sorted_operations = sort_operations_by_date(operations, reverse=True)
        if sorted_operations:
            print(f"Первая отсортированная операция: {sorted_operations[0].get('date')}")