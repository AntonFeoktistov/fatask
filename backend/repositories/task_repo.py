from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.task import Task
from backend.models.user import User
from backend.repositories.user_repo import UserRepository
from backend.schemas.task import TaskCreate


class TaskRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(self.db)

    async def get_task_or_none_by_id(self, task_id: int) -> Task | None:
        query = await self.db.execute(
            select(Task).where(
                Task.id == task_id,
            )
        )
        return query.scalar_one_or_none()

    async def get_task_or_none(self, user_id: int, title: str) -> Task | None:
        query = await self.db.execute(
            select(Task).where(Task.title == title, Task.user_id == user_id)
        )
        return query.scalar_one_or_none()

    async def get_user_tasks(self, user_id: int) -> list[Task]:
        query = await self.db.execute(select(Task).where(Task.user_id == user_id))
        return query.scalars().all()

    async def create_task(self, task_data: TaskCreate, user: User) -> Task:
        new_task = Task(
            title=task_data.title, description=task_data.description, user=user
        )
        self.db.add(new_task)
        return new_task
