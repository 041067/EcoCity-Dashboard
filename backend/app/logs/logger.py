import logging
import sys
from typing import Any


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
        msg = super().format(record)
        level = record.levelname
        return f"[{level}] {record.name}: {record.getMessage()}"


logger = setup_logger()
