import functools
import logging
import sys


def log(filename=None):
    """
    Декоратор для логирования начала и конца выполнения функции,
    а также ее результатов или возникших ошибок.

    Args:
        filename (str, optional): Имя файла для записи логов.
        Если не указано, логи выводятся в консоль.
    """

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')


    for handler in list(logger.handlers):
        logger.removeHandler(handler)

    if filename:
        file_handler = logging.FileHandler(filename, mode='a', encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    else:
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
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
    @log(filename="example.log")
    def example_function_to_file(a, b):
        """Пример функции для логирования в файл."""
        return a + b

    @log()
    def example_function_to_console(text):
        """Пример функции для логирования в консоль."""
        print(f"Внутри функции: {text}")
        return f"Обработано: {text}"

    example_function_to_file(5, 3)
    example_function_to_console("Тестовое сообщение")
