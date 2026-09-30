import logging

from backend.tasks.celery_app import celery_app
from backend.tasks.email_client import send_email

logger = logging.getLogger(__name__)


@celery_app.task(
    name="backend.tasks.email_tasks.send_welcome_email",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
)
def send_welcome_email(self, to_email: str, username: str) -> str:
    try:
        body = (
            f"Hi {username},\n\n"
            f"Welcome to Fatask — your personal task tracker!\n\n"
            f"Start by adding your first task.\n\n"
            f"— Fatask team"
        )
        send_email(
            to=to_email,
            subject="Welcome to Fatask!",
            body=body,
        )
        return f"sent to {to_email}"
    except Exception as exc:
        logger.exception("Failed to send welcome email to %s", to_email)
        raise self.retry(exc=exc)


@celery_app.task(name="backend.tasks.email_tasks.send_daily_reports")
def send_daily_reports() -> str:
    logger.info("Daily report job started")

    # 1. Получить всех пользователей и их задачи за сутки
    # 2. Для каждого сформировать данные для LLM
    # 3. Вызвать LLM (синхронный httpx.Client)
    # 4. Отправить email

    # Пока заглушка:
    return "daily reports job finished (stub)"
