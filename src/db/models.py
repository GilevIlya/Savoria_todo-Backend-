from datetime import date, datetime
import enum

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from uuid import UUID as pyuuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import text, String, func
from db.types import DDMMYYYY


class Base(DeclarativeBase):
    pass

class TaskStatus(enum.Enum):
    NOT_STARTED = 'Not Started'
    IN_PROGRESS = 'In Progress'
    DONE = 'Done'

class TaskPriority(enum.Enum):
    LOW = 'Low'
    MODERATE = 'Moderate'
    EXTREME = 'Extreme'

class UsersTable(Base):
    __tablename__ = 'users'

    id: Mapped[pyuuid] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        server_default=text("gen_random_uuid()") )
    firstname: Mapped[str] = mapped_column(nullable=True)
    lastname: Mapped[str] = mapped_column(nullable=True)
    username: Mapped[str] = mapped_column(nullable=True, unique=True)
    email: Mapped[str] = mapped_column(nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(512), nullable=True)
    google_sub: Mapped[str] = mapped_column(String(256), nullable=True, unique=True)


class TasksTable(Base):
    __tablename__ = 'tasks'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[pyuuid] = mapped_column(UUID(as_uuid=True))
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str] = mapped_column(String(1000), nullable=False)
    status: Mapped[TaskStatus]
    priority: Mapped[TaskPriority]
    deadline: Mapped[date] = mapped_column(DDMMYYYY, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        server_default= func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )