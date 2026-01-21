from fastapi import HTTPException
from db.engine import SessionDep
from sqlalchemy import select, update
from sqlalchemy.engine.row import Row as AlchemyRow
from db.models import UsersTable


async def selecting_data_by_uuid(
        uuid: str,
        session: SessionDep) -> AlchemyRow:
    async with session.begin():
        query = select(UsersTable.firstname,
                        UsersTable.lastname,
                        UsersTable.email).where(UsersTable.id == uuid)
        result = await session.execute(query)
        user_info = result.one_or_none()
        if user_info is None:
                raise ValueError('User not found')
        return user_info
    

async def update_user_data(
        user_uuid: str, 
        session: SessionDep, 
        new_creds: dict):
    try:
        stmt = update(UsersTable).where(UsersTable.id == user_uuid).values(**new_creds)

        await session.execute(stmt)
        await session.commit()

    except:
        raise HTTPException(status_code=404)
    

async def set_profile_pic_db(
        user_uuid: str,
        picture_url: str,
        session: SessionDep
):
    async with session.begin():
        stmt = update(
            UsersTable
        ).where(
            UsersTable.id == user_uuid).values(
            profile_pic = picture_url
        )
        await session.execute(stmt)

async def get_profile_pic(
        user_uuid: str,
        session: SessionDep
):
    async with session.begin():
        query = select(
            UsersTable.profile_pic
        ).where(
            UsersTable.id == user_uuid
        )
        result = await session.execute(query)
        return {
            'profile_pic': result.scalar_one_or_none()
        }