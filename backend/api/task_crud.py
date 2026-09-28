import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import get_db
from backend.core.dependencies import get_current_user
from backend.models.user import User
from backend.schemas.task import TaskCreate, TaskResponse, TaskUpdate
from backend.services.task_service import TaskService

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.post(
    "",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_task(
    task_data: TaskCreate,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TaskResponse:
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
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
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
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[TaskResponse]:
    task_service = TaskService(db)
    tasks = await task_service.get_all_users_tasks(user)
    return tasks


@router.patch(
    "/{task_oid}",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
)
async def update_task(
    task_oid: uuid.UUID,
    task_data: TaskUpdate,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TaskResponse:
    task_service = TaskService(db)
    updated_task = await task_service.update_task(task_oid, task_data, user)
    return updated_task


@router.delete(
    "/{task_oid}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_task(
    task_oid: uuid.UUID,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    task_service = TaskService(db)
    await task_service.delete_task(task_oid, user)
