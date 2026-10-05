import smtplib
from email.message import EmailMessage

from loguru import logger

from backend.core.config import settings

SMTP_HOST = settings.SMTP_HOST
SMTP_PORT = settings.SMTP_PORT
SMTP_FROM = settings.SMTP_FROM
SMTP_USER = settings.SMTP_USER
SMTP_PASSWORD = settings.SMTP_PASSWORD
SMTP_USE_TLS = settings.SMTP_USE_TLS


def send_email(to: str, subject: str, body: str, html: str | None = None) -> None:
    msg = EmailMessage()
    msg["From"] = SMTP_FROM
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)

    if html:
        msg.add_alternative(html, subtype="html")

    logger.info("Sending email to {} | subject={}", to, subject)

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as server:
            if SMTP_USE_TLS:
                server.starttls()
            if SMTP_USER and SMTP_PASSWORD:
                server.login(SMTP_USER, SMTP_PASSWORD)

            server.send_message(msg)

        logger.success("Email sent to {} | subject={}", to, subject)

    except smtplib.SMTPAuthenticationError:
        logger.error("SMTP auth failed | user={}", SMTP_USER)
        raise

    except smtplib.SMTPConnectError:
        logger.error("SMTP connect failed | host={} | port={}", SMTP_HOST, SMTP_PORT)
        raise

    except Exception as e:
        logger.error("Email send failed | to={} | error={}", to, e)
        raise
