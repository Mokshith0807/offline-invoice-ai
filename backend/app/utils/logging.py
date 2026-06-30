import os
import sys
import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler

from app.core.config import settings


def setup_logging():
    log_level = logging.DEBUG if settings.debug else logging.INFO

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)

    log_file = settings.logs_dir / "app.log"
    file_handler = RotatingFileHandler(
        str(log_file), maxBytes=10 * 1024 * 1024, backupCount=5
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    for lib_logger in ["uvicorn", "uvicorn.access", "fastapi", "httpx"]:
        logging.getLogger(lib_logger).setLevel(logging.WARNING)

    return logging.getLogger(__name__)
