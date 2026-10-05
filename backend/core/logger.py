import logging
import sys

from loguru import logger


class InterceptHandler(logging.Handler):
    """Перехватывает логи из стандартного logging и направляет их в Loguru."""

    def emit(self, record: logging.LogRecord) -> None:
        # Получаем уровень лога, соответствующий Loguru
        try:
            level: str | int = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Ищем кадр вызова (кто вызвал лог)
        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_logging():
    """Настраивает Loguru как единый логгер для всего проекта."""
    # Удаляем дефолтный handler Loguru
    logger.remove()

    # Логи в консоль (человекочитаемый формат)
    logger.add(
        sys.stdout,
        level="DEBUG",
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        ),
        colorize=True,
    )

    # Логи в файл (ротация: 10 МБ, хранить 7 дней)
    logger.add(
        "logs/app.log",
        level="INFO",
        rotation="10 MB",
        retention="7 days",
        compression="gz",
        format=(
            "{time:YYYY-MM-DD HH:mm:ss} | "
            "{level: <8} | "
            "{name}:{function}:{line} | "
            "{message}"
        ),
    )

    # Перехватываем логи Celery, httpx и других библиотем
    for name in ("celery", "httpx", "kafka"):
        logging.getLogger(name).handlers = [InterceptHandler()]
        logging.getLogger(name).propagate = True

    # Перехватываем root logger
    logging.basicConfig(handlers=[InterceptHandler()], level=logging.INFO, force=True)

    return logger
