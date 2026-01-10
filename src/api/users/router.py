from fastapi import APIRouter, Header, Response, Depends
from api.users.service import return_data_for_dashboard
from db.engine import SessionDep
from redis_utils.client import get_redis
from api.users.service import logout, update_user_credentials
from api.users.schemas import UserUpdateSchema
from redis.asyncio import Redis

from time import perf_counter

users_router = APIRouter(prefix='/users')

@users_router.get('/user_data')
async def get_dashboard_data(
        session: SessionDep, 
        authorization: str = Header(None, alias="Authorization")):
    return await return_data_for_dashboard(
        session=session,
        authorization=authorization
    )

@users_router.delete('/logout')
async def logout_user(response: Response):
    await logout(response=response)

@users_router.patch('/update_data')
async def update_user_payload(
        session: SessionDep,
        new_data: UserUpdateSchema,
        authorization: str = Header(None, alias="Authorization")):
    update_creds = new_data.dict(exclude_unset=True)
    await update_user_credentials(
        access_token=authorization, 
        session=session, 
        new_creds=update_creds)
    return {
        'update data': 'success'
    }

@users_router.post("/test_redis/{your_name}")
async def test_redis(
    your_name: str,
    redis: Redis = Depends(get_redis)
):
    now = perf_counter()
    await redis.set(your_name, 'Hello')
    print(perf_counter() - now)
    return {
        await redis.get(your_name)
    }