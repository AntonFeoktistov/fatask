from celery import Celery
from celery.schedules import crontab

from backend.core.config import settings
from backend.core.logger import setup_logging

logger = setup_logging()

RABBITMQ_URL = settings.RABBITMQ_URL

celery_app = Celery(
    "fatask",
    broker=RABBITMQ_URL,
    backend="rpc://",
    include=[
        "backend.tasks.email_tasks",
        "backend.tasks.email_llm",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    broker_connection_retry_on_startup=True,
    result_expires=3600,
    # Отключаем стандартный логгер Celery — Loguru перехватит
    worker_hijack_root_logger=False,
)

celery_app.conf.beat_schedule = {
    "daily-task-report": {
        "task": "backend.tasks.email_tasks.send_daily_reports",
        "schedule": crontab(hour=0, minute=0),
    },
}

logger.info("Celery app initialized | broker={}", RABBITMQ_URL)
