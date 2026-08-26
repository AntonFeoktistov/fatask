from typing import Annotated

from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import get_db, settings

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
)


@app.get("/")
async def root():
    return {
        "message": "Hello World",
        "app": settings.app_name,
        "version": settings.app_version,
    }


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/users")
async def get_users(db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(text("SELECT COUNT(*) FROM users"))
    count = result.scalar()
    return {"count": count}
