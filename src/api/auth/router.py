from fastapi import APIRouter, Response, Depends, Request, Body
from api.auth.schemas import RegisterSchema, LoginSchema
from db.engine import SessionDep
from argon2 import PasswordHasher
from api.security_tools.passwordhasher import get_password_hasher
from api.auth.google_auth_service import get_google_oauth, GoogleOAuth
from api.auth.crud import register_user, authenticate_user, authenticate_google_user, check_if_uuid_exists
from api.auth_jwt.service import get_jwt_token_service_obj, JwtTokenService, get_uuid_from_cookie
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
                      password_hasher: PasswordHasher=Depends(get_password_hasher),
                      token_service: JwtTokenService=Depends(get_jwt_token_service_obj)):
    user_uuid = await authenticate_user(payload=payload, session=session, password_hasher=password_hasher)
    if user_uuid:
        access_token = await token_service.create_tokens(user_uuid=user_uuid, response=response, agree_status=payload.agree)
        return access_token
    
@auth_router.get('/refresh')
async def refresh_access_token(request: Request, session: SessionDep,
                               token_service: JwtTokenService=Depends(get_jwt_token_service_obj)):
    uuid = await get_uuid_from_cookie(request=request)
    await check_if_uuid_exists(uuid=uuid, session=session)
    new_access_token = await token_service.generate_access_token(user_uuid=uuid)

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
    google_oauth_obj: GoogleOAuth=Depends(get_google_oauth),
    token_service: JwtTokenService=Depends(get_jwt_token_service_obj)
    ):
    token_data = await google_oauth_obj.exchange_code_for_token(code=code)
    user_data = await google_oauth_obj.parse_id_token(id_token=token_data['id_token'])

    user_uuid = await authenticate_google_user(user_data=user_data, session=data_base_session)
    if user_uuid:
        tokens = await token_service.create_tokens(user_uuid=user_uuid, response=fastapi_response, agree_status=True)
        return tokens
    return {"error": "Authentication failed"}