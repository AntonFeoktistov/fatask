import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import get_db
from backend.core.dependencies import get_current_user
from backend.models.user import User
from backend.schemas.task import TaskCreate, TaskResponse
from backend.services.task_service import TaskService

router = APIRouter(prefix="/api/task", tags=["task"])


@router.post(
    "",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_task(
    task_data: TaskCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    task_service = TaskService(db)
    new_task = await task_service.create_task(user, task_data)
    return new_task


@router.get(
    "/{task_oid}",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
)
async def get_task(
    task_oid: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
) -> TaskResponse:
    task_service = TaskService(db)
    task = await task_service.get_task_by_oid(task_oid, user)
    return task


@router.get(
    "",
    response_model=list[TaskResponse],
    status_code=status.HTTP_200_OK,
)
async def get_all_users_tasks(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
) -> TaskResponse:
    task_service = TaskService(db)
    tasks = await task_service.get_all_users_tasks(user)
    return tasks
