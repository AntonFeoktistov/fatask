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
        task = self.task_repo.get_task_or_none(user_id=user.id, title=task_data.title)
        if task:
            raise TaskAlreadyExistsException()

        task = await self.task_repo.create_task(user_id=user.id, task_data=task_data)

        await self.db.commit()
        await self.db.refresh(task)
        return task

    async def get_user_tasks(self, user: User) -> list[Task]:
        return await self.task_repo.get_user_tasks(user.id)

    async def get_task_by_id(self, task_id: int, user: User) -> Task:
        task = await self.task_repo.get_task_or_none_by_id(task_id)
        if not task:
            raise TaskIsNotFoundException()
        if task.user_id != user.id:
            raise TaskIsNotFoundException()
        return task

    async def update_task(
        self, task_id: int, user: User, task_data: TaskUpdate
    ) -> Task:
        task = await self.get_task_by_id(task_id, user)
        updated = await self.task_repo.update(task, task_data)
        await self.db.commit()
        await self.db.refresh(updated)
        return updated

    async def delete_task(self, task_id: int, user: User) -> None:
        task = await self.get_task_by_id(task_id, user)
        await self.task_repo.delete(task)
        await self.db.commit()
