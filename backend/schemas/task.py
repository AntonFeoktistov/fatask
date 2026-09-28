import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from backend.core.config import settings


class TaskCreate(BaseModel):
    title: str = Field(
        ...,
        min_length=1,
        max_length=settings.MAX_TASK_TITLE_LEN,
        strip_whitespace=True,
        pattern=r"^\S.*$",
    )
    description: str = Field(
        default="",
        max_length=settings.MAX_TASK_DESCRIPTION_LEN,
        strip_whitespace=True,
    )


class TaskUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=settings.MAX_TASK_TITLE_LEN,
        pattern=r"^\S.*$",
    )
    description: str | None = Field(
        default=None,
        max_length=settings.MAX_TASK_DESCRIPTION_LEN,
    )


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    oid: uuid.UUID
    title: str
    description: str | None
    created_at: datetime
    updated_at: datetime
