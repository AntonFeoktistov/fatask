from fastapi import FastAPI

from backend.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
)


@app.get("/")
async def root():
    return {"message": f"Welcome to {settings.app_name}!"}
