import functools
import logging


def log(filename=None):
    """
    Декоратор для логирования начала и конца выполнения функции,
    а также ее результатов или возникших ошибок.

    Args:
        filename (str, optional): Имя файла для записи логов.
                                   Если не указано, логи выводятся в консоль.
                                   Defaults to None.
    """
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        filename=filename)
    logger = logging.getLogger()

    def decorator(func):
        """Внутренний декоратор."""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            """Обертка для декорируемой функции."""
            logger.info(f"Начало выполнения функции: {func.__name__}")
            try:
                result = func(*args, **kwargs)
                logger.info(f"{func.__name__} ok. Результат: {result}")
                return result
            except Exception as e:
                logger.error(f"{func.__name__} error: {type(e).__name__}. Inputs: {args}, {kwargs}")
                raise
            finally:
                logger.info(f"Завершение выполнения функции: {func.__name__}")
        return wrapper
    return decorator


if __name__ == '__main__':
    @log(filename="mylog.txt")
    def example_function(a, b):
        """Пример функции для тестирования логирования в файл."""
        return a / b

    @log()
    def another_function(text):
        """Пример функции для тестирования логирования в консоль."""
        print(f"Выполнена функция another_function с текстом: {text}")
        return f"Обработано: {text}"

    try:
        example_function(10, 2)
        example_function(5, 0)
    except ZeroDivisionError:
        print("Поймана ошибка деления на ноль.")

    another_function("Привет!")
