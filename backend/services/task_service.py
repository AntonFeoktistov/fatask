import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.exceptions import TaskAlreadyExistsException, TaskIsNotFoundException
from backend.models.task import Task
from backend.models.user import User
from backend.repositories.task_repo import TaskRepository
from backend.repositories.user_repo import UserRepository
from backend.schemas.task import TaskCreate, TaskUpdate


class TaskService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.task_repo = TaskRepository(db)
        self.user_repo = UserRepository(db)

    async def create_task(self, user: User, task_data: TaskCreate) -> Task:
        task = await self.task_repo.get_task_or_none(
            user_oid=user.oid, title=task_data.title
        )
        if task:
            raise TaskAlreadyExistsException()

        task = await self.task_repo.create_task(user=user, task_data=task_data)

        await self.db.commit()
        await self.db.refresh(task)
        return task

    async def get_all_users_tasks(self, user: User) -> list[Task]:
        return await self.task_repo.get_user_tasks(user.oid)

    async def get_task_by_oid(self, task_oid: uuid.UUID, user: User) -> Task:
        task = await self.task_repo.get_task_or_none_by_oid(task_oid)
        if not task:
            raise TaskIsNotFoundException()
        if task.user_oid != user.oid:
            raise TaskIsNotFoundException()
        return task

    async def update_task(
        self,
        task_oid: uuid.UUID,
        task_data: TaskUpdate,
        user: User,
    ) -> Task:
        task = await self.get_task_by_oid(task_oid, user)
        if not task:
            raise TaskIsNotFoundException()

        if task_data.title is not None:
            task.title = task_data.title
        if task_data.description is not None:
            task.description = task_data.description
        if task_data.is_done is not None:
            task.is_done = task_data.is_done
        await self.db.commit()
        await self.db.refresh(task)
        return task

    async def delete_task(self, task_oid: uuid.UUID, user: User) -> None:
        task = await self.get_task_by_oid(task_oid, user)
        if not task:
            raise TaskIsNotFoundException()
        await self.db.delete(task)
        await self.db.commit()
