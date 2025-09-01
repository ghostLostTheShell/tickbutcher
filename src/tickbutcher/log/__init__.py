import logging
from logging.handlers import TimedRotatingFileHandler
import os
from .formatter import COLOR_FORMATTER, fmt
from typing import Optional


file_handler: Optional[TimedRotatingFileHandler] = None


def init_file_handler():
    global file_handler
    log_path = "log/app.log"
    if os.path.exists(os.path.dirname(log_path)) is False:
        os.mkdir(os.path.dirname(log_path))
    file_handler = TimedRotatingFileHandler(log_path, when="D", interval=1, backupCount=7, encoding="utf-8")
    file_handler.setFormatter(logging.Formatter(fmt))
    file_handler.doRollover()  # Clear log content by triggering a rollover

ch_handler = logging.StreamHandler()
ch_handler.setFormatter(COLOR_FORMATTER)

logger = logging.getLogger("root")
# logger.addHandler(file_handler)
logger.addHandler(ch_handler)
logger.setLevel(logging.DEBUG)

def file_logger_enable():
  if file_handler is None:
    init_file_handler()
  
  logger.addHandler(file_handler) # type: ignore

def file_logger_disable():
    logger.removeHandler(file_handler) # type: ignore

__all__ = ["logger"]