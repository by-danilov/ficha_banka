import pytest
import os
from src.decorators import log
import logging


def get_log_records(filename):
    """Вспомогательная функция для чтения записей из лог-файла."""
    with open(filename, 'r', encoding='utf-8') as f:
        return f.read()


def test_log_to_console_success(capsys):
    """Тест логирования в консоль при успешном выполнении функции."""
    @log()
    def success_func():
        return "Успех!"

    result = success_func()
    captured = capsys.readouterr()
    assert "Начало выполнения функции: success_func" in captured.out
    assert "success_func ok. Результат: Успех!" in captured.out
    assert "Завершение выполнения функции: success_func" in captured.out
    assert result == "Успех!"


def test_log_to_console_error(capsys):
    """Тест логирования ошибки в консоль."""
    @log()
    def error_func():
        raise ValueError("Тестовая ошибка")

    with pytest.raises(ValueError, match="Тестовая ошибка"):
        error_func()

    captured = capsys.readouterr()
    assert "Начало выполнения функции: error_func" in captured.out
    assert "error_func error: ValueError. Inputs: (), {}" in captured.err or captured.out
    assert "Завершение выполнения функции: error_func" in captured.out


def test_log_to_file_success(tmp_path):
    """Тест логирования в файл при успешном выполнении функции."""
    log_file = str(tmp_path / "success.log")

    @log(filename=log_file)
    def file_success_func(a, b):
        return a * b

    result = file_success_func(2, 3)
    log_content = get_log_records(log_file)
    assert "Начало выполнения функции: file_success_func" in log_content
    assert "file_success_func ok. Результат: 6" in log_content
    assert "Завершение выполнения функции: file_success_func" in log_content
    assert result == 6


def test_log_to_file_error(tmp_path):
    """Тест логирования ошибки в файл."""
    log_file = str(tmp_path / "error.log")

    @log(filename=log_file)
    def file_error_func(x):
        return 10 / x

    with pytest.raises(ZeroDivisionError):
        file_error_func(0)

    log_content = get_log_records(log_file)
    assert "Начало выполнения функции: file_error_func" in log_content
    assert "file_error_func error: ZeroDivisionError. Inputs: (0,), {}" in log_content
    assert "Завершение выполнения функции: file_error_func" in log_content


def teardown_module():
    """Удаляет временные лог-файлы после тестов."""
    paths = ["example.log", "success.log", "error.log"]
    for path in paths:
        if os.path.exists(path):
            os.remove(path)
