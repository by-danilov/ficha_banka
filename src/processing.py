def filter_by_state(data: list, state: str = "EXECUTED") -> list:
    """Принимает список словарей с банковскими операциями и фильтрует по значению 'state'."""
    return [item for item in data if item.get("state") == state]


def sort_by_date(data: list, descending: bool = True) -> list:
    """Принимает список словарей с операциями и сортирует по ключу 'date'."""
    return sorted(data, key=lambda item: item.get("date", ""), reverse=descending)
