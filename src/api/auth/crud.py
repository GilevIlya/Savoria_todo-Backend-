from fastapi import HTTPException
from fastapi.concurrency import run_in_threadpool
from db.engine import SessionDep
from sqlalchemy import select, insert, exists
from argon2 import PasswordHasher
from api.auth.schemas import RegisterSchema, LoginSchema
from db.models import UsersTable
from sqlalchemy.dialects.postgresql import insert as postgresql_insert

async def register_user(payload: RegisterSchema, session: SessionDep, password_hasher: PasswordHasher):
    hashed_password = await run_in_threadpool(password_hasher.hash, payload.password)
    payload.password = hashed_password
    query = select(UsersTable).where(
        (UsersTable.email == payload.email) | (UsersTable.username == payload.username)
    )
    result = await session.execute(query)
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(status_code=409, detail='such email/username exists')
    
    await insert_user_creds(payload=payload, session=session)
    return {'success': 'user has been added'}
    
async def insert_user_creds(payload: RegisterSchema, session: SessionDep):
    insert_user = insert(UsersTable).values(
        payload.model_dump()
    )
    await session.execute(insert_user)
    await session.commit()

async def authenticate_user(payload: LoginSchema, session: SessionDep,
                            password_hasher: PasswordHasher):
    query = select(UsersTable.id, UsersTable.password).where(
        (UsersTable.username == payload.username)
    )
    result = await session.execute(query)
    existing_user = result.one_or_none()
    if not existing_user:
        raise HTTPException(status_code=401, detail='Unauthorized, incorrect data')
    
    try:
        await run_in_threadpool(password_hasher.verify, existing_user.password, payload.password)
    except:
        raise HTTPException(status_code=401, detail='Unauthorized, incorrect data')
    
    return existing_user.id

async def authenticate_google_user(
        user_data: dict, session: SessionDep,):
    query = postgresql_insert(UsersTable).values(
        **user_data
    ).on_conflict_do_update(
        index_elements=[UsersTable.google_sub],
        set_={
        "firstname": postgresql_insert(UsersTable).excluded.firstname,
        "lastname": postgresql_insert(UsersTable).excluded.lastname,
        "profile_pic": postgresql_insert(UsersTable).excluded.profile_pic
    }
    ).returning(UsersTable.id)

    res = await session.execute(query)
    user_id = res.scalar_one_or_none()
    await session.commit()

    return user_id

async def check_if_uuid_exists(uuid, session: SessionDep):
    try:
        query = select(exists().where(UsersTable.id == uuid))
        result = await session.execute(query)
        if_exists = result.scalar_one_or_none()
        if not if_exists:
            raise HTTPException(status_code=404, detail='No user with such uuid exists')
        return True
    except:
        raise HTTPException(status_code=401, detail='Cookie is invalid, redirect to sign_up')