import uuid

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True
    )
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    username: Mapped[str] = mapped_column(
        String(100), unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    tasks: Mapped[list["Task"]] = relationship(  # noqa: F821
        "Task",
        back_populates="user",
        lazy="selectin",
        primaryjoin="User.id == Task.user_id",
    )

    def __repr__(self) -> str:
        return f"<User {self.username} ({self.email})>"
