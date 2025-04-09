import logging
import sys

from loguru import logger


class _InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        try:
            level: str | int = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
        logger.opt(depth=6, exception=record.exc_info).log(level, record.getMessage())


def setup_logging(level: str = "INFO", json_format: bool = False) -> None:
    """Направляет логи stdlib (uvicorn, httpx) в loguru и настраивает формат вывода."""
    logger.remove()
    logger.add(sys.stderr, level=level, serialize=json_format, backtrace=False, diagnose=False)
    logging.basicConfig(handlers=[_InterceptHandler()], level=0, force=True)
    for name in ("uvicorn", "uvicorn.access", "uvicorn.error"):
        logging.getLogger(name).handlers = [_InterceptHandler()]
        logging.getLogger(name).propagate = False
    logging.getLogger("httpx").setLevel(logging.WARNING)
