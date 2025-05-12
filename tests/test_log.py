import pytest
import os
from decorators import log


def test_log_to_console(capsys):
    """Тест логирования в консоль при успешном выполнении функции."""
    @log()
    def example_function(a, b):
        """Простая функция сложения для теста."""
        return a + b

    result = example_function(3, 5)
    captured = capsys.readouterr()
    assert "Начало выполнения функции: example_function" in captured.out
    assert "example_function ok. Результат: 8" in captured.out
    assert "Завершение выполнения функции: example_function" in captured.out
    assert result == 8


def test_log_to_file(tmp_path):
    """Тест логирования в файл при успешном выполнении функции."""
    log_file = tmp_path / "test.log"

    @log(filename=str(log_file))
    def another_function(text):
        """Функция для обработки текста и логирования в файл."""
        return f"Обработано: {text}"

    result = another_function("тест")
    with open(log_file, "r") as f:
        log_content = f.read()
        assert "Начало выполнения функции: another_function" in log_content
        assert "another_function ok. Результат: обработано: тест" in log_content
        assert "Завершение выполнения функции: another_function" in log_content
    assert result == "обработано: тест"


def test_log_error_to_console(capsys):
    """Тест логирования ошибки в консоль."""
    @log()
    def failing_function(x):
        """Функция, вызывающая ZeroDivisionError."""
        return 1 / x

    with pytest.raises(ZeroDivisionError):
        failing_function(0)

    captured = capsys.readouterr()
    assert "Начало выполнения функции: failing_function" in captured.out
    assert "failing_function error: ZeroDivisionError. Inputs: (0,), {}" in captured.err
    assert "Завершение выполнения функции: failing_function" in captured.out


def test_log_error_to_file(tmp_path):
    """Тест логирования ошибки в файл."""
    log_file = tmp_path / "error.log"

    @log(filename=str(log_file))
    def another_failing_function(a, b):
        """Функция, вызывающая ValueError."""
        raise ValueError("Что-то пошло не так")

    with pytest.raises(ValueError, match="Что-то пошло не так"):
        another_failing_function(1, 2)

    with open(log_file, "r") as f:
        log_content = f.read()
        assert "Начало выполнения функции: another_failing_function" in log_content
        assert "another_failing_function error: ValueError. Inputs: (1, 2), {}" in log_content
        assert "Завершение выполнения функции: another_failing_function" in log_content


def teardown_module():
    """Удаляет временный лог-файл mylog.txt после тестов."""
    if os.path.exists("mylog.txt"):
        os.remove("mylog.txt")
