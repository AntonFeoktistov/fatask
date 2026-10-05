import asyncio
import uuid

from faststream.kafka import KafkaBroker
from loguru import logger
from sqlalchemy import select

from backend.core.database import AsyncSessionLocal
from backend.models.task import Task
from backend.models.user import User
from backend.tasks.celery_app import celery_app
from backend.tasks.email_client import send_email

KAFKA_URL = "kafka:29092"

# Глобальный брокер и очередь ответов
_broker = KafkaBroker(KAFKA_URL)
_pending: dict[str, asyncio.Future] = {}


@_broker.subscriber("report-responses")
async def _on_response(msg: dict):
    logger.debug("Kafka response received | raw={}", msg)
    correlation_id = msg.get("correlation_id")
    if correlation_id and correlation_id in _pending:
        future = _pending.pop(correlation_id)
        if not future.done():
            report = msg.get("report", "")
            logger.info(
                "Report matched | correlation_id={} | report_length={}",
                correlation_id,
                len(report),
            )
            future.set_result(report)
        else:
            logger.warning("Future already done | correlation_id={}", correlation_id)
    else:
        logger.warning(
            "Unknown correlation_id in response | correlation_id={}",
            correlation_id,
        )


async def _request_llm_report(tasks_data: dict) -> str:
    correlation_id = str(uuid.uuid4())
    future: asyncio.Future = asyncio.get_event_loop().create_future()
    _pending[correlation_id] = future

    logger.info(
        "Requesting LLM report | user={} | correlation_id={} | total={} | done={} | undone={}",
        tasks_data["email"],
        correlation_id,
        tasks_data["total"],
        tasks_data["done"],
        tasks_data["undone"],
    )

    await _broker.publish(
        {
            "user_email": tasks_data["email"],
            "total": tasks_data["total"],
            "done": tasks_data["done"],
            "undone": tasks_data["undone"],
            "done_titles": tasks_data["done_titles"],
            "undone_tasks": tasks_data["undone_tasks"],
            "correlation_id": correlation_id,
        },
        "report-requests",
    )
    logger.debug("Published to report-requests | correlation_id={}", correlation_id)

    try:
        report = await asyncio.wait_for(future, timeout=60)
        logger.success(
            "LLM report received | correlation_id={} | length={}",
            correlation_id,
            len(report),
        )
        return report
    except asyncio.TimeoutError:
        _pending.pop(correlation_id, None)
        logger.error(
            "LLM report timeout (60s) | correlation_id={} | user={}",
            correlation_id,
            tasks_data["email"],
        )
        raise TimeoutError("LLM report timeout")


async def _collect_users_data() -> list[dict]:
    logger.info("Collecting users data from database")

    async with AsyncSessionLocal() as session:
        users_result = await session.execute(select(User))
        users = users_result.scalars().all()
        logger.info("Found {} users", len(users))

        result = []
        for user in users:
            tasks_result = await session.execute(
                select(Task).where(Task.user_oid == user.oid)
            )
            tasks = tasks_result.scalars().all()
            done = [t for t in tasks if t.is_done]
            undone = [t for t in tasks if not t.is_done]

            user_data = {
                "email": user.email,
                "username": user.username,
                "total": len(tasks),
                "done": len(done),
                "undone": len(undone),
                "done_titles": [t.title for t in done],
                "undone_tasks": [
                    {"title": t.title, "description": t.description} for t in undone
                ],
            }
            logger.debug(
                "User data | email={} | total={} | done={} | undone={}",
                user.email,
                len(tasks),
                len(done),
                len(undone),
            )
            result.append(user_data)

        return result


async def _send_daily_reports_async() -> str:
    logger.info("Starting daily reports pipeline")
    await _broker.start()
    logger.debug("Kafka broker started")

    try:
        users_data = await _collect_users_data()
        sent = 0
        skipped = 0
        failed = 0

        for data in users_data:
            if data["total"] == 0:
                skipped += 1
                logger.info("Skipping user (no tasks) | email={}", data["email"])
                continue

            try:
                report = await _request_llm_report(data)
                await asyncio.to_thread(
                    send_email,
                    to=data["email"],
                    subject="Your daily task report",
                    body=report,
                )
                sent += 1
                logger.success(
                    "Report sent | email={} | report_length={}",
                    data["email"],
                    len(report),
                )
            except TimeoutError:
                failed += 1
                logger.error("Skipped (LLM timeout) | email={}", data["email"])
            except Exception as e:
                failed += 1
                logger.exception(
                    "Failed to send report | email={} | error={}",
                    data["email"],
                    e,
                )

        summary = f"reports sent: {sent}, skipped: {skipped}, failed: {failed}"
        logger.info("Daily reports completed | {}", summary)
        return summary

    finally:
        await _broker.stop()
        logger.debug("Kafka broker stopped")


@celery_app.task(name="backend.tasks.email_tasks.send_daily_reports")
def send_daily_reports() -> str:
    logger.info("Celery task send_daily_reports invoked")
    try:
        result = asyncio.run(_send_daily_reports_async())
        logger.success("Celery task finished | result={}", result)
        return result
    except Exception as e:
        logger.error("Celery task failed | error={}", e)
        raise
