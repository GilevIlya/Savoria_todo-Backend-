from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from db.config import data_base_config
from db.models import Base

engine = create_async_engine(
    url=data_base_config.DATABASE_url_asyncpg,
    echo=False)

session_factory = async_sessionmaker(
    bind=engine,
    expire_on_commit=False
    )

async def get_session():
    async with session_factory() as session:
        yield session

async def create_user_table():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

SessionDep = Annotated[AsyncSession, Depends(get_session)]