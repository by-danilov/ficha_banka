import json
import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
file_handler = logging.FileHandler(
    os.path.join(log_dir, "utils.log"), mode="w", encoding="utf-8"
)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


def load_operations_from_json(json_filepath: str) -> list[dict]:
    """
    Загружает список финансовых операций из JSON файла,
    фильтруя некорректные или неполные записи.
    """
    if not os.path.exists(json_filepath):
        logger.error(f"JSON файл не найден: {json_filepath}")
        return []

    try:
        with open(json_filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, list):
                logger.error(
                    f"JSON файл {json_filepath} содержит некорректный формат данных (ожидается список)."
                )
                return []

            operations = []
            # Определите все обязательные поля, включая вложенные
            required_top_level_keys = [
                "id",
                "state",
                "date",
                "operationAmount",
                "description",
            ]
            # 'from' и 'to' могут отсутствовать

            for i, item in enumerate(data):
                if not isinstance(item, dict):
                    logger.warning(
                        f"Элемент {i + 1} в JSON-файле не является словарем: {item}. Пропускаю."
                    )
                    continue

                # Проверка обязательных верхнеуровневых ключей и их значений на None
                missing_top_keys = [
                    key
                    for key in required_top_level_keys
                    if key not in item or item[key] is None
                ]
                if missing_top_keys:
                    logger.warning(
                        f"Элемент {i + 1} (ID: {item.get('id')}) в JSON-файле не содержит все обязательные верхнеуровневые ключи или их значения None ({missing_top_keys}). Пропускаю."
                    )
                    continue

                # Проверка operationAmount и currency
                op_amount = item.get("operationAmount")
                if not isinstance(op_amount, dict):
                    logger.warning(
                        f"Элемент {i + 1} (ID: {item.get('id')}) в JSON-файле: 'operationAmount' не является словарем. Пропускаю."
                    )
                    continue

                required_op_amount_keys = ["amount", "currency"]
                missing_op_amount_keys = [
                    key
                    for key in required_op_amount_keys
                    if key not in op_amount or op_amount[key] is None
                ]
                if missing_op_amount_keys:
                    logger.warning(
                        f"Элемент {i + 1} (ID: {item.get('id')}) в JSON-файле: некорректный или неполный 'operationAmount' ({missing_op_amount_keys}). Пропускаю."
                    )
                    continue

                currency_info = op_amount.get("currency")
                if not isinstance(currency_info, dict):
                    logger.warning(
                        f"Элемент {i + 1} (ID: {item.get('id')}) в JSON-файле: 'currency' не является словарем. Пропускаю."
                    )
                    continue

                required_currency_keys = ["name", "code"]
                missing_currency_keys = [
                    key
                    for key in required_currency_keys
                    if key not in currency_info or currency_info[key] is None
                ]
                if missing_currency_keys:
                    logger.warning(
                        f"Элемент {i + 1} (ID: {item.get('id')}) в JSON-файле: некорректная или неполная 'currency' информация ({missing_currency_keys}). Пропускаю."
                    )
                    continue

                operations.append(item)

            logger.info(
                f"Успешно загружено {len(operations)} операций из JSON файла: {json_filepath}."
            )
            return operations
    except json.JSONDecodeError as e:
        logger.error(f"Ошибка декодирования JSON файла {json_filepath}: {e}")
        return []
    except Exception as e:
        logger.error(f"Неожиданная ошибка при чтении JSON файла {json_filepath}: {e}")
        return []


def sort_operations_by_date(
    operations: list[dict], reverse: bool = False
) -> list[dict]:
    """
    Сортирует список финансовых операций по дате.
    Дата может быть в различных форматах ISO (с Z, без Z, только дата) или DD.MM.YYYY.
    Операции с некорректными или отсутствующими датами будут отфильтрованы.
    """

    def parse_date(date_str: str) -> datetime:
        # Убедимся, что все даты являются наивными для корректного сравнения
        if date_str is None or not isinstance(date_str, str) or not date_str.strip():
            raise ValueError("Пустая или некорректная строка даты")

        # Попытка парсинга ISO формата с Z
        try:
            dt_obj = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
            return dt_obj.replace(tzinfo=None)  # Делаем наивной
        except ValueError:
            pass

        # Попытка парсинга DD.MM.YYYY формата
        try:
            return datetime.strptime(date_str, "%d.%m.%Y")
        except ValueError:
            pass

        # Попытка парсинга ISO формата (без Z или с Z, но используя fromisoformat)
        # fromisoformat может обрабатывать как даты, так и даты со временем и смещением
        try:
            dt_obj = datetime.fromisoformat(
                date_str.replace("Z", "+00:00")
            )  # Нормализуем Z для fromisoformat
            return dt_obj.replace(tzinfo=None)  # Делаем наивной
        except ValueError:
            pass

        # Если ни один формат не подошел
        raise ValueError(f"Не удалось распознать формат даты: '{date_str}'")

    try:
        processed_operations = []
        for op in operations:
            if "date" in op and op["date"]:
                try:
                    parsed_date = parse_date(op["date"])
                    op_copy = op.copy()  # Копируем операцию, чтобы не изменять оригинал
                    op_copy["_parsed_date"] = (
                        parsed_date  # Добавляем временный ключ для сортировки
                    )
                    processed_operations.append(op_copy)
                except ValueError as e:
                    logger.warning(
                        f"Пропущена операция с ID {op.get('id')} из-за нераспознанного формата даты '{op.get('date')}': {e}"
                    )
            else:
                logger.warning(
                    f"Пропущена операция с ID {op.get('id')} из-за отсутствия или пустой даты."
                )

        sorted_ops = sorted(
            processed_operations, key=lambda x: x["_parsed_date"], reverse=reverse
        )

        # Удаляем временный ключ после сортировки и возвращаем только исходные поля
        final_sorted_ops = []
        for op_copy in sorted_ops:
            op_copy_clean = op_copy.copy()
            if "_parsed_date" in op_copy_clean:
                del op_copy_clean["_parsed_date"]
            final_sorted_ops.append(op_copy_clean)

        logger.info(
            f"Операции отсортированы по дате (обратный порядок: {reverse}). Количество отсортированных: {len(final_sorted_ops)}"
        )
        return final_sorted_ops
    except Exception as e:
        logger.error(f"Произошла ошибка при сортировке операций: {e}")
        # В случае глобальной ошибки, возвращаем копию исходного списка (без фильтрации)
        return list(
            operations
        )  # Это может быть неожиданно, лучше возвращать [] или отсортированный на момент ошибки список.
        # Возвращаем пустой список, если произошла критическая ошибка сортировки
        # ИЛИ возвращаем processed_operations, если сортировка на них не упала
        # Давайте здесь вернем отфильтрованные, но неотсортированные операции, если произошла ошибка *сортировки*,
        # а не парсинга. Если упала сортировка, то список processed_operations содержит элементы, которые не удалось отсортировать.
        # В случае ошибки на этапе sorted(), лучше вернуть пустой список, так как результат будет непредсказуем.
        return []
