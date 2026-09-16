from fastapi import FastAPI

from backend.api.auth import router as auth_router
from backend.api.task_crud import router as task_router
from backend.core.database import settings

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
)

app.include_router(auth_router)
app.include_router(task_router)


@app.get("/")
async def root():
    return {
        "message": "Hello World",
        "app": settings.app_name,
        "version": settings.app_version,
    }
