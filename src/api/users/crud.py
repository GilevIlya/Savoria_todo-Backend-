from fastapi import HTTPException
from src.utils.database_engine import SessionDep
from sqlalchemy import select
from src.utils.create_tables import UsersTable
from uuid import UUID


async def selecting_data_by_uuid(uuid: UUID, session: SessionDep):
    try:
        query = select(UsersTable.firstname,
                    UsersTable.lastname,
                    UsersTable.email).where(UsersTable.id == uuid)
        result = await session.execute(query)
        existing_user = result.one_or_none()
        if existing_user is None:
            raise HTTPException(status_code=401, detail='Is not registered')
        return existing_user
    except:
        raise HTTPException(status_code=401, detail='No such user by access token')