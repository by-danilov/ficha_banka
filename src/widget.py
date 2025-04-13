from masks import get_mask_card_number, get_mask_account

def mask_input_string(data: str) -> str:
    """Принимает строку с типом и номером, возвращает замаскированную строку."""
    parts = data.split()
    if len(parts) < 2:
        raise ValueError("Неверный формат входной строки. Ожидается 'Тип Номер'.")

    prefix = ' '.join(parts[:-1])
    number = parts[-1]

    if prefix.lower().startswith("счет"):
        masked_number = get_mask_account(number)
    else:
        masked_number = get_mask_card_number(number)

    return f"{prefix} {masked_number}"
