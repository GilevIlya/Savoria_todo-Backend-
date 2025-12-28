from fastapi import APIRouter, Header, Response
from api.users.service import return_data_for_dashboard, get_user_uuid
from database_engine import SessionDep
from api.users.service import logout, update_user_credentials
from api.users.schemas import UserUpdateSchema
from api.users.crud import update_user_data

users_router = APIRouter(prefix='/users')

@users_router.get('/user_data')
async def get_dashboard_data(
        session: SessionDep, 
        authorization: str = Header(None, alias="Authorization")):
    return await return_data_for_dashboard(
        session=session,
        authorization=authorization
    )

@users_router.get('/logout')
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