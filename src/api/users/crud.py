from fastapi import HTTPException
from db.engine import SessionDep
from sqlalchemy import select, update
from db.models import UsersTable
from uuid import UUID


async def selecting_data_by_uuid(uuid: UUID, session: SessionDep) -> tuple:
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
        raise HTTPException(status_code=404, detail='No such user by access token')
    

async def update_user_data(user_uuid: str, session: SessionDep, new_creds: dict):
    try:
        stmt = update(UsersTable).where(UsersTable.id == user_uuid).values(**new_creds)

        await session.execute(stmt)
        await session.commit()

    except:
        raise HTTPException(status_code=404)