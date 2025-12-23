from fastapi import APIRouter, Response, Depends, Request, Body
from src.api.auth.schemas import RegisterSchema, LoginSchema
from src.utils.database_engine import SessionDep
from argon2 import PasswordHasher
from src.api.security_tools.passwordhasher import get_password_hasher
from src.api.auth.google_auth_service import get_google_oauth, GoogleOAuth
from src.api.auth.crud import register_user, authenticate_user, authenticate_google_user, check_if_uuid_exists
from src.jwt.jwt_auth import create_tokens, uuid_from_cookie, create_only_access_token
from typing import Annotated

auth_router = APIRouter(prefix='/auth')

@auth_router.post('/sign_up')
async def signup_user(payload: RegisterSchema, session: SessionDep,
                      password_hasher: PasswordHasher=Depends(get_password_hasher)):
    result = await register_user(payload=payload, session=session, password_hasher=password_hasher)
    return result

@auth_router.post('/sign_in')
async def signin_user(payload: LoginSchema, response: Response, 
                      session: SessionDep,
                      password_hasher: PasswordHasher=Depends(get_password_hasher)):
    result = await authenticate_user(payload=payload, session=session, password_hasher=password_hasher)
    if result:
        access_token = await create_tokens(user_uuid=result, response=response, agree_status=payload.agree)
        return access_token
    
@auth_router.get('/refresh')
async def refresh_access_token(request: Request, session: SessionDep):
    uuid = await uuid_from_cookie(request=request)
    await check_if_uuid_exists(uuid=uuid, session=session)
    new_access_token = await create_only_access_token(uuid=uuid)

    return {
        'access_token': new_access_token
    }

@auth_router.get('/google/redirect')
async def create_google_auth_form(google_oauth_obj: GoogleOAuth=Depends(get_google_oauth)):
    return {
        'url': google_oauth_obj.get_auth_url()
    }


@auth_router.post('/google/callback')
async def handle_google_code(
    code: Annotated[str, Body(embed=True)],
    data_base_session: SessionDep, fastapi_response: Response,
    google_oauth_obj: GoogleOAuth=Depends(get_google_oauth)
    ):
    token_data = await google_oauth_obj.exchange_code_for_token(code=code)
    user_data = await google_oauth_obj.parse_id_token(id_token=token_data['id_token'])

    user_uuid = await authenticate_google_user(user_data=user_data, session=data_base_session)
    if user_uuid:
        tokens = await create_tokens(user_uuid=user_uuid, response=fastapi_response, agree_status=True)
        return tokens
    return {"error": "Authentication failed"}