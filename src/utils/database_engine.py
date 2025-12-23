from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from src.utils.config import data_base_config


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

SessionDep = Annotated[AsyncSession, Depends(get_session)]