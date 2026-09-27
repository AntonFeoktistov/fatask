import uuid

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
    oid: uuid.UUID
    title: str = Field(
        min_length=1,
        max_length=settings.MAX_TASK_TITLE_LEN,
        strip_whitespace=True,
        pattern=r"^\S.*$",
    )
    description: str = Field(
        max_length=settings.MAX_TASK_DESCRIPTION_LEN,
        strip_whitespace=True,
    )


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    oid: uuid.UUID
    title: str
    description: str
