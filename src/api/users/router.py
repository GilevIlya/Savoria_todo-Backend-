from fastapi import APIRouter, Header
from src.api.users.service import return_data_for_dashboard
from src.utils.database_engine import SessionDep

users_router = APIRouter(prefix='/users')

@users_router.get("/user_data")
async def get_dashboard_data(
        session: SessionDep, 
        authorization: str = Header(None, alias="Authorization")):
    return await return_data_for_dashboard(
        session=session,
        authorization=authorization
    )