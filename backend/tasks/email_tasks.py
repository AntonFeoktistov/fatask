from loguru import logger

from backend.tasks import email_llm  # noqa
from backend.tasks.celery_app import celery_app
from backend.tasks.email_client import send_email


@celery_app.task(
    name="backend.tasks.email_tasks.send_welcome_email",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
)
def send_welcome_email(self, to_email: str, username: str) -> str:
    logger.info(
        "Welcome email task started | to={} | username={} | attempt={}",
        to_email,
        username,
        self.request.retries + 1,
    )

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
        logger.success("Welcome email sent | to={}", to_email)
        return f"sent to {to_email}"

    except Exception as exc:
        logger.error(
            "Welcome email failed | to={} | attempt={} | error={}",
            to_email,
            self.request.retries + 1,
            exc,
        )
        if self.request.retries >= self.max_retries:
            logger.error(
                "Max retries ({}) reached for {} | giving up",
                self.max_retries,
                to_email,
            )
        raise self.retry(exc=exc)
