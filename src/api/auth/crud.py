from argon2 import PasswordHasher
from argon2.exceptions import InvalidHash, VerifyMismatchError
from fastapi.concurrency import run_in_threadpool
from pydantic import EmailStr
from sqlalchemy import exists, insert, select
from sqlalchemy.dialects.postgresql import insert as postgresql_insert
from sqlalchemy.exc import IntegrityError

from api.auth.schemas import LoginSchema, RegisterSchema
from db.engine import SessionDep
from db.models import UsersTable


async def register_user(
    payload: RegisterSchema, 
    session: SessionDep, 
    password_hasher: PasswordHasher
) -> dict:
    async with session.begin():
        hashed_password = await run_in_threadpool(password_hasher.hash, payload.password)

        query = select(UsersTable).where(
            (UsersTable.email == payload.email) | (UsersTable.username == payload.username)
        )
        result = await session.execute(query)
        existing_user = result.scalar_one_or_none()

        if existing_user:
            raise IntegrityError()    
        
        await insert_user_creds(
            session=session,
            firstname=payload.firstname,
            lastname=payload.lastname,
            password=hashed_password)

        return {
                "success": "user has been added"
            }


async def insert_user_creds( 
    session: SessionDep,
    firstname: str,
    lastname: str,
    username: str,
    password: str,
    email: EmailStr,
) -> None:
    insert_user = insert(UsersTable).values(
        firstname=firstname,
        lastname=lastname,
        username=username,
        password=password,
        email=email
    )
    await session.execute(insert_user)



async def authenticate_user(
    payload: LoginSchema, 
    session: SessionDep, 
    password_hasher: PasswordHasher
) -> str:
    async with session.begin():
        query = select(UsersTable.id, UsersTable.password).where(
            (UsersTable.username == payload.username)
        )
        result = await session.execute(query)
        existing_user = result.one_or_none()

    if not existing_user:
        raise ValueError("No such user")

    try:
        await run_in_threadpool(
            password_hasher.verify, existing_user.password, payload.password
        )
    except (InvalidHash, VerifyMismatchError):
        raise InvalidHash()

    return existing_user.id


async def authenticate_google_user(
    user_data: dict,
    session: SessionDep,
) -> str:
    async with session.begin():
        query = (
            postgresql_insert(UsersTable)
            .values(**user_data)
            .on_conflict_do_update(
                index_elements=[UsersTable.google_sub],
                set_={"google_sub": postgresql_insert(UsersTable).excluded.google_sub},
            )
            .returning(UsersTable.id)
        )

        res = await session.execute(query)
        user_id = res.scalar_one_or_none()

    return user_id


async def check_if_uuid_exists(
    uuid, 
    session: SessionDep
) -> bool:
    async with session.begin():
        query = select(exists().where(UsersTable.id == uuid))
        result = await session.execute(query)
        if_exists = result.scalar_one_or_none()
    if not if_exists:
        raise ValueError("No user with such uuid exists")
    return True