import logging
import os
import re

# Создаем логгер для модуля masks
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Создаем обработчик для записи логов в файл
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
file_handler = logging.FileHandler(os.path.join(log_dir, "masks.log"), mode="w")

# Создаем форматтер
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)

# Добавляем обработчик к логгеру
logger.addHandler(file_handler)


def mask_card_number(card_number):
    """Маскирует номер банковской карты, оставляя видимыми только последние 4 цифры."""
    if not isinstance(card_number, str) or not re.match(r"^\d{13,19}$", card_number):
        logger.error(f"Попытка маскировки некорректного номера карты: '{card_number}'")
        return "Некорректный номер карты"
    masked_part = "*" * (len(card_number) - 4)
    masked_number = masked_part + card_number[-4:]
    logger.debug(
        f"Замаскирован номер карты: '{masked_number}' (исходный: '{card_number[:6]}...{card_number[-4:]}')"
    )
    return masked_number


def mask_account_number(account_number):
    """Маскирует номер счета, оставляя видимыми только последние 4 цифры."""
    if not isinstance(account_number, str) or not re.match(r"^\d{10}$", account_number):
        logger.error(
            f"Попытка маскировки некорректного номера счета: '{account_number}'"
        )
        return "Некорректный номер счета"
    masked_part = "*" * (len(account_number) - 4)
    masked_number = masked_part + account_number[-4:]
    logger.debug(
        f"Замаскирован номер счета: '{masked_number}' (исходный: '{account_number[:3]}...{account_number[-4:]}')"
    )
    return masked_number


if __name__ == "__main__":
    card = "1234567890123456"
    masked_card = mask_card_number(card)
    print(f"Замаскированная карта: {masked_card}")

    invalid_card = "123"
    masked_invalid_card = mask_card_number(invalid_card)
    print(f"Маскировка некорректной карты: {masked_invalid_card}")

    account = "9876543210"
    masked_account = mask_account_number(account)
    print(f"Замаскированный счет: {masked_account}")

    invalid_account = "123"
    masked_invalid_account = mask_account_number(invalid_account)
    print(f"Маскировка некорректного счета: {masked_invalid_account}")
