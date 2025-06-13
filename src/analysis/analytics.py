# src/analysis/analytics.py
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Добавляем FileHandler только если он еще не добавлен, чтобы избежать дублирования
if not any(
    isinstance(handler, logging.FileHandler)
    and handler.baseFilename.endswith("analytics.log")
    for handler in logger.handlers
):
    import os

    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    file_handler = logging.FileHandler(
        os.path.join(log_dir, "analytics.log"), mode="w", encoding="utf-8"
    )
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


def get_transactions_by_date(
    transactions: list[dict], target_date_str: str
) -> list[dict]:
    """
    Фильтрует список транзакций, возвращая только те, которые произошли в указанную дату.
    Args:
        transactions (list[dict]): Список словарей, представляющих транзакции.
        target_date_str (str): Целевая дата в формате 'ДД.ММ.ГГГГ'.
    Returns:
        list[dict]: Список транзакций, произошедших в указанную дату.
    """
    filtered_transactions = []
    try:
        target_date = datetime.strptime(target_date_str, "%d.%m.%Y").date()
        logger.debug(f"Поиск транзакций за дату: {target_date_str}")
        for transaction in transactions:
            try:
                transaction_date_str = transaction.get("date")
                if transaction_date_str:
                    transaction_date = datetime.strptime(
                        transaction_date_str, "%d.%m.%Y"
                    ).date()
                    if transaction_date == target_date:
                        filtered_transactions.append(transaction)
            except ValueError:
                logger.warning(
                    f"Некорректный формат даты в транзакции: {transaction.get('date')}. Пропущена."
                )
                continue
            except TypeError:
                logger.warning(
                    f"Тип данных даты в транзакции некорректен: {transaction.get('date')}. Пропущена."
                )
                continue
        logger.info(
            f"Найдено {len(filtered_transactions)} транзакций за {target_date_str}."
        )
    except ValueError:
        logger.error(
            f"Некорректный формат целевой даты: '{target_date_str}'. Ожидается ДД.ММ.ГГГГ."
        )
    except Exception as e:
        logger.error(f"Произошла ошибка при фильтрации транзакций по дате: {e}")
    return filtered_transactions


def get_card_number_masked(card_number: str) -> str:
    """
    Маскирует номер карты, оставляя открытыми первые 6 и последние 4 цифры.
    Пример: "Visa Platinum 7000 79** **** 6361"
    """
    if not isinstance(card_number, str) or not card_number.strip():
        logger.warning(
            f"Получен некорректный номер карты для маскировки: '{card_number}'"
        )
        return "Неизвестная карта"

    parts = card_number.split()
    name_parts = []
    number_part = ""

    # Отделяем название карты от номера
    for part in parts:
        if (
            part.isdigit() and len(part) == 16
        ):  # Предполагаем, что полный номер карты - 16 цифр
            number_part = part
        elif (
            part.isdigit() and len(part) == 19 and part.count("*") > 0
        ):  # Может быть уже частично маскирован
            number_part = part.replace(
                "*", ""
            )  # Убираем звездочки для корректного маскирования
        elif part.isdigit() and (
            len(part) == 4 or len(part) == 6
        ):  # Если номер уже разбит на части
            number_part += part
        else:
            name_parts.append(part)

    if (
        not number_part
    ):  # Если номер не найден в явном виде, попробуем обработать всю строку
        cleaned_number = "".join(filter(str.isdigit, card_number))
        if len(cleaned_number) >= 16:
            number_part = cleaned_number[
                -16:
            ]  # Берем последние 16 цифр, если их больше
            name_parts = [card_number.replace(number_part, "").strip()]
        else:
            logger.warning(
                f"Номер карты слишком короткий для маскировки: '{card_number}'"
            )
            return card_number  # Возвращаем как есть, если слишком короткий

    # Если номер найден, убедимся, что он имеет достаточную длину для маскирования
    if (
        len(number_part) >= 16
    ):  # Требуется минимум 16 цифр для стандартного маскирования
        masked_number = (
            f"{number_part[:4]} {number_part[4:6]}** **** {number_part[-4:]}"
        )
    elif (
        len(number_part) >= 10
    ):  # Если номер короче 16, но достаточно длинный для частичной маскировки
        masked_number = f"{number_part[:6]}******{number_part[-4:]}"
    else:
        logger.warning(f"Недостаточно цифр для маскировки карты: '{number_part}'")
        return card_number  # Возвращаем как есть

    name = " ".join(name_parts) if name_parts else "Карта"

    # Дополнительная проверка на случай, если название карты было некорректно отделено
    if "Счет" in name:  # Если это счет, то маскируем как счет
        return get_account_number_masked(card_number)

    logger.debug(f"Маскирование карты: '{card_number}' -> '{name} {masked_number}'")
    return f"{name} {masked_number}".strip()


def get_account_number_masked(account_number: str) -> str:
    """
    Маскирует номер счета, оставляя открытыми только последние 4 цифры.
    Пример: "Счет **4506"
    """
    if not isinstance(account_number, str) or not account_number.strip():
        logger.warning(
            f"Получен некорректный номер счета для маскировки: '{account_number}'"
        )
        return "Неизвестный счет"

    cleaned_number = "".join(filter(str.isdigit, account_number))

    if len(cleaned_number) >= 4:
        masked_number = f"**{cleaned_number[-4:]}"
    else:
        logger.warning(f"Недостаточно цифр для маскировки счета: '{account_number}'")
        return account_number  # Возвращаем как есть, если слишком короткий

    # Добавляем "Счет" в начало, если его нет
    if "Счет" not in account_number:
        logger.debug(
            f"Маскирование счета: '{account_number}' -> 'Счет {masked_number}'"
        )
        return f"Счет {masked_number}"
    else:
        # Если "Счет" уже присутствует, заменяем номер
        parts = account_number.split()
        if len(parts) > 1 and parts[0] == "Счет":
            logger.debug(
                f"Маскирование счета: '{account_number}' -> 'Счет {masked_number}'"
            )
            return f"Счет {masked_number}"
        else:
            logger.debug(
                f"Маскирование счета: '{account_number}' -> '{account_number.replace(cleaned_number, masked_number)}'"
            )
            return account_number.replace(cleaned_number, masked_number)


if __name__ == "__main__":
    # Примеры использования и тестирование
    print("Тестирование get_transactions_by_date:")
    sample_transactions = [
        {
            "id": 1,
            "date": "14.03.2023",
            "description": "Оплата",
            "amount": 100,
            "currency": "RUB",
        },
        {
            "id": 2,
            "date": "15.03.2023",
            "description": "Перевод",
            "amount": 200,
            "currency": "USD",
        },
        {
            "id": 3,
            "date": "14.03.2023",
            "description": "Покупка",
            "amount": 50,
            "currency": "RUB",
        },
    ]

    today_transactions = get_transactions_by_date(sample_transactions, "14.03.2023")
    print(f"Транзакции за 14.03.2023: {today_transactions}")

    no_transactions = get_transactions_by_date(sample_transactions, "16.03.2023")
    print(f"Транзакции за 16.03.2023: {no_transactions}")

    print("\nТестирование get_card_number_masked:")
    print(
        f"Visa Platinum 7000792296156361: {get_card_number_masked('Visa Platinum 7000792296156361')}"
    )
    print(
        f"Maestro 781084** **** 5568: {get_card_number_masked('Maestro 781084******5568')}"
    )
    print(f"7810841234565568: {get_card_number_masked('7810841234565568')}")
    print(
        f"American Express 123456789012345: {get_card_number_masked('American Express 123456789012345')}"
    )  # Менее 16 цифр
    print(f"Просто текст: {get_card_number_masked('Просто текст')}")
    print(f"Пустая строка: {get_card_number_masked('')}")
    print(f"None: {get_card_number_masked(None)}")  # type: ignore

    print("\nТестирование get_account_number_masked:")
    print(
        f"Счет 40812345678901234506: {get_account_number_masked('Счет 40812345678901234506')}"
    )
    print(f"40812345678901234506: {get_account_number_masked('40812345678901234506')}")
    print(f"Счет 1234: {get_account_number_masked('Счет 1234')}")
    print(f"123: {get_account_number_masked('123')}")  # Менее 4 цифр
    print(f"Пустая строка: {get_account_number_masked('')}")
    print(f"None: {get_account_number_masked(None)}")  # type: ignore
