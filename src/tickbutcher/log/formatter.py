# ANSI 转义码（终端颜色代码）
import logging
import sys

fmt = "[%(asctime)s] [%(name)s] [%(process)d] [%(levelname)s] %(message)s"

RESET = "\033[0m"
COLORS = {
    'DEBUG': "\033[36m",  # 青色
    'INFO': "\033[32m",   # 绿色
    'WARNING': "\033[33m",  # 黄色
    'ERROR': "\033[31m",   # 红色
    'CRITICAL': "\033[41m", # 红色背景
}

class _ColorFormatter(logging.Formatter):
    """带颜色的日志格式化器"""

    def __init__(self, fmt=None, datefmt=None, use_color=True):
        super().__init__(fmt, datefmt)
        self.use_color = use_color and sys.stdout.isatty()  # 仅在终端启用颜色

    def format(self, record):
        log_color = COLORS.get(record.levelname, RESET) if self.use_color else ""
        reset_color = RESET if self.use_color else ""

        # 格式化日志
        log_message = super().format(record)
        return f"{log_color}{log_message}{reset_color}"
      
COLOR_FORMATTER = _ColorFormatter(
    fmt=fmt,
    datefmt="%Y-%m-%d %H:%M:%S"
)