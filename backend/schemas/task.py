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
    id: int
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
    id: int
    title: str
    description: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
