from pathlib import Path
import sys
from datetime import datetime

from loguru import logger as _logger



_print_level = "INFO"


def define_log_level(print_level="INFO", logfile_level="DEBUG", name: str = None):
    """Adjust the log level to above level"""
    global _print_level
    _print_level = print_level

    # 动态获取当前项目的根目录
    current_project_root = Path(__file__).resolve().parent.parent.parent
    logs_dir = current_project_root / "logs"
    logs_dir.mkdir(exist_ok=True)  # 确保 logs 目录存在

    current_date = datetime.now()
    formatted_date = current_date.strftime("%Y%m%d%H%M%S")
    log_name = (
        f"{name}_{formatted_date}" if name else formatted_date
    )  # name a log with prefix name

    _logger.remove()
    _logger.add(sys.stderr, level=print_level)
    _logger.add(logs_dir / f"{log_name}.log", level=logfile_level)
    return _logger


logger = define_log_level("DEBUG")


if __name__ == "__main__":
    logger.info("Starting application")
    logger.debug("Debug message")
    logger.warning("Warning message")
    logger.error("Error message")
    logger.critical("Critical message")

    try:
        raise ValueError("Test error")
    except Exception as e:
        logger.exception(f"An error occurred: {e}")
