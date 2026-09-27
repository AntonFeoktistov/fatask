import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core import security
from backend.models.user import User
from backend.schemas.user import UserCreate


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_or_none_by_oid(self, user_oid: uuid.UUID) -> User | None:
        query = await self.db.execute(
            select(User).where(
                User.oid == user_oid,
            )
        )
        return query.scalar_one_or_none()

    async def get_user_or_none_by_email(self, email: str) -> User | None:
        query = await self.db.execute(
            select(User).where(
                User.email == email,
            )
        )
        return query.scalar_one_or_none()

    async def get_user_or_none_by_username(self, username: str) -> User | None:
        query = await self.db.execute(
            select(User).where(
                User.username == username,
            )
        )
        return query.scalar_one_or_none()

    async def create_user(self, user_data: UserCreate) -> User:
        new_user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=security.get_password_hash(user_data.password),
        )
        self.db.add(new_user)
        return new_user
