import logging
import sys


def setup_logger(name: str = "ecocity") -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(CustomFormatter())
        logger.addHandler(handler)

    return logger


class CustomFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        level = record.levelname
        return f"[{level}] {record.name}: {record.getMessage()}"


logger = setup_logger()
