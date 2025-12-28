from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from uuid import UUID as pyuuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import text, String

class Base(DeclarativeBase):
    pass

class UsersTable(Base):
    __tablename__ = 'users'

    id: Mapped[pyuuid] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        server_default=text("gen_random_uuid()") )
    firstname: Mapped[str] = mapped_column(nullable=False)
    lastname: Mapped[str] = mapped_column(nullable=False)
    username: Mapped[str] = mapped_column(nullable=True)
    email: Mapped[str] = mapped_column(nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(512), nullable=True)
    google_sub: Mapped[str] = mapped_column(String(256), nullable=True, unique=True)
