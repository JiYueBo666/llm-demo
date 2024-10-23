import time
from functools import wraps


def time_logger(func):
    logger=get_green_logger()
    #@wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        logger.info(
            f"Function '{func.__name__}' executed in {end_time - start_time:.4f} seconds."
        )
        return result

    return wrapper


def get_green_logger():
    import logging

    class GreenFormatter(logging.Formatter):
        def format(self, record):
            record.msg = f"\033[32m{record.msg}\033[0m"  # ANSI escape code for green
            return super().format(record)

    logger = logging.getLogger("logger")
    if not logger.handlers:  # 检查是否已经有处理器被添加
        handler = logging.StreamHandler()
        formatter = GreenFormatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


def get_debug_logger():
    import logging

    class YellowFormatter(logging.Formatter):
        def format(self, record):
            record.msg = f"\033[33m{record.msg}\033[0m"  # ANSI escape code for yellow
            return super().format(record)

    logger = logging.getLogger("yellow_logger")
    handler = logging.StreamHandler()
    formatter = YellowFormatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger
