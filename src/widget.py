from src.masks import mask_account_number, mask_card_number


def mask_input_string(data: str) -> str:
    """Принимает строку с типом и номером, возвращает замаскированную строку."""
    parts = data.split()
    if len(parts) < 2:
        raise ValueError("Неверный формат входной строки. Ожидается 'Тип Номер'.")

    prefix = ' '.join(parts[:-1])
    number = parts[-1]

    if prefix.lower().startswith("счет"):
        masked_number = mask_account_number(number)
    else:
        masked_number = mask_card_number(number)

    return f"{prefix} {masked_number}"


def get_date(date_str: str) -> str:
    """Преобразуем дату в привычный формат"""
    date_part = date_str.split("T")[0]
    date_elements = date_part.split("-")
    year = date_elements[0]
    month = date_elements[1]
    day = date_elements[2]
    return f"{day}.{month}.{year}"
