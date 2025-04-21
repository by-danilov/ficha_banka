
# 🧾 Project: Transaction Filter & Sorter

## 📌 Цель проекта

Этот мини-проект предназначен для обработки списков банковских транзакций. Он включает в себя:

- Фильтрацию транзакций по статусу
- Сортировку транзакций по дате
- Маскировку номеров счетов и карт
- Преобразование дат в человекочитаемый формат

---

## 🛠 Установка

Проект не требует установки внешних библиотек. Всё работает на **Python 3.7+**.

```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
```

---

## 🚀 Использование

Импортируй функции:

```python
from processing import (
    filter_by_state,
    sort_by_date
)

from widget import (
    mask_input_string,
    get_date
)
```

---

## 🗃 Основные функции

### 🔍 `filter_by_state(data, state='EXECUTED')`

Фильтрует список транзакций по полю `state`.

```python
executed = filter_by_state(data)
canceled = filter_by_state(data, 'CANCELED')
```

---

### 🗂 `sort_by_date(data, descending=True)`

Сортирует список транзакций по полю `date`.

```python
sorted_data = sort_by_date(data)  # по убыванию
sorted_data_asc = sort_by_date(data, descending=False)  # по возрастанию
```

---

### 🛡 `mask_input_string(data: str) -> str`

Маскирует номер карты или счёта.  
Определяет тип по ключевому слову в начале строки:

- **"Счет 40817810099910004312"** → `Счет **4312`
- **"Visa Platinum 1234567890123456"** → `Visa Platinum 1234 56** **** 3456`

```python
masked = mask_input_string("Visa Classic 1234567812345678")
# "Visa Classic 1234 56** **** 5678"
```

> Функция использует вспомогательные функции `get_mask_card_number()` и `get_mask_account()` из модуля `masks`.

---

### 📅 `get_date(date_str: str) -> str`

Преобразует дату из ISO-формата в привычный `ДД.ММ.ГГГГ`:

```python
print(get_date("2019-07-03T18:35:29.512364"))
# "03.07.2019"
```


---

## 📂 Пример данных

```python
data = [
    {'id': 1, 'state': 'EXECUTED', 'date': '2023-01-01T12:00:00.000000'},
    {'id': 2, 'state': 'CANCELED', 'date': '2022-12-01T09:00:00.000000'}
]
```

---

## 🤝 Автор
Данилов Никита (ТГ: @by_danilov)
