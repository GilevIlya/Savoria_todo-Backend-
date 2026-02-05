import enum
from datetime import date, datetime
from uuid import UUID as pyuuid

from sqlalchemy import String, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from db.types import DDMMYYYY


class Base(DeclarativeBase):
    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class TaskStatus(enum.Enum):
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"


class TaskPriority(enum.Enum):
    LOW = "LOW"
    MODERATE = "MODERATE"
    EXTREME = "EXTREME"


class UsersTable(Base):
    __tablename__ = "users"

    id: Mapped[pyuuid] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    firstname: Mapped[str] = mapped_column(nullable=True)
    lastname: Mapped[str] = mapped_column(nullable=True)
    username: Mapped[str] = mapped_column(nullable=True, unique=True)
    email: Mapped[str] = mapped_column(nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(512), nullable=True)
    google_sub: Mapped[str] = mapped_column(String(256), nullable=True, unique=True)
    profile_pic: Mapped[str] = mapped_column(nullable=True)


class TasksTable(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[pyuuid] = mapped_column(UUID(as_uuid=True))
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str] = mapped_column(String(1000), nullable=False)
    status: Mapped[TaskStatus] = mapped_column(
        server_default=TaskStatus.NOT_STARTED.value
    )
    priority: Mapped[TaskPriority] = mapped_column(
        server_default=TaskPriority.LOW.value
    )
    deadline: Mapped[date] = mapped_column(DDMMYYYY, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now(), nullable=False
    )


class CompletedTasksTable(Base):
    __tablename__ = "completed_tasks"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    user_id: Mapped[pyuuid] = mapped_column(UUID(as_uuid=True))
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str] = mapped_column(String(1000), nullable=False)
    status: Mapped[TaskStatus] = mapped_column(server_default=TaskStatus.DONE.value)
    priority: Mapped[TaskPriority] = mapped_column(
        server_default=TaskPriority.LOW.value
    )
    deadline: Mapped[date] = mapped_column(DDMMYYYY, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now(), nullable=False
    )
