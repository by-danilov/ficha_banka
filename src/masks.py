def get_mask_card_number(card_number: str) -> str:
    """Функция принимает номер карты и маскирует его"""
    # Проверка, что номер карты состоит из 16 цифр
    if len(card_number) != 16 or not card_number.isdigit():
        raise ValueError("Номер карты должен содержать ровно 16 цифр.")

    # Формирование маски
    masked_number = card_number[:6] + "" + "******" + "" + card_number[-4:]

    # Разбивка на блоки по 4 цифры
    masked_number = " ".join(
        [masked_number[i: i + 4] for i in range(0, len(masked_number), 4)]
    )

    return masked_number


def get_mask_account(account_number: str) -> str:
    """Функция принимает номер счета и маскирует его"""
    # Проверка, что номер счета состоит из цифр
    if not account_number.isdigit():
        raise ValueError("Номер счета должен содержать только цифры.")

    # Все, кроме последних четырех цифр маскируется **
    masked_account = "**" + account_number[-4:]

    return masked_account
