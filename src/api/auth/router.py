from typing import Annotated

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHash
from fastapi import APIRouter, Body, Depends, HTTPException, Request, Response
from sqlalchemy.exc import IntegrityError

from api.auth.auth_jwt.service import (JwtTokenService,
                                       get_jwt_token_service_obj,
                                       get_uuid_from_cookie)

from api.auth.crud import (authenticate_google_user, authenticate_user,
                           check_if_uuid_exists, register_user)

from api.auth.google_auth_service import GoogleOAuth, get_google_oauth
from api.auth.schemas import LoginSchema, RegisterSchema
from api.auth.security_tools.passwordhasher import get_password_hasher
from db.engine import SessionDep

auth_router = APIRouter(prefix="/auth")


@auth_router.post("/sign_up")
async def signup_user(
    payload: RegisterSchema,
    session: SessionDep,
    password_hasher: PasswordHasher = Depends(get_password_hasher),
):
    try:
        result = await register_user(
            payload=payload, 
            session=session, 
            password_hasher=password_hasher
        )
        return result
    except IntegrityError:
        raise HTTPException(status_code=409, detail='User already exists')


@auth_router.post("/sign_in")
async def signin_user(
    payload: LoginSchema,
    response: Response,
    session: SessionDep,
    password_hasher: PasswordHasher = Depends(get_password_hasher),
    token_service: JwtTokenService = Depends(get_jwt_token_service_obj),
):
    try:
        user_uuid = await authenticate_user(
            payload=payload, 
            session=session, 
            password_hasher=password_hasher
        )
    except ValueError:
        raise HTTPException(status_code=401, detail='Invalid creds')
    except InvalidHash:
        raise HTTPException(status_code=401, detail='Invalid password')
    if user_uuid:
        access_token = await token_service.create_tokens(
            user_uuid=user_uuid, 
            response=response, 
            agree_status=payload.agree
        )
    return access_token


@auth_router.get("/refresh")
async def refresh_access_token(
    request: Request,
    session: SessionDep,
    token_service: JwtTokenService = Depends(get_jwt_token_service_obj),
):
    try:
        uuid = await get_uuid_from_cookie(request=request)

        await check_if_uuid_exists(
            uuid=uuid, 
            session=session
        )
    except ValueError:
        raise HTTPException(status_code=401, detail='No user with such uuid')
    new_access_token = await token_service.generate_access_token(user_uuid=uuid)

    return {"access_token": new_access_token}


@auth_router.get("/google/redirect")
async def create_google_auth_form(
    google_oauth_obj: GoogleOAuth = Depends(get_google_oauth),
):
    return {"url": google_oauth_obj.get_auth_url()}


@auth_router.post("/google/callback")
async def handle_google_code(
    code: Annotated[str, Body(embed=True)],
    data_base_session: SessionDep,
    fastapi_response: Response,
    google_oauth_obj: GoogleOAuth = Depends(get_google_oauth),
    token_service: JwtTokenService = Depends(get_jwt_token_service_obj),
):
    token_data = await google_oauth_obj.exchange_code_for_token(code=code)
    user_data = await google_oauth_obj.parse_id_token(id_token=token_data["id_token"])

    user_uuid = await authenticate_google_user(
        user_data=user_data, 
        session=data_base_session
    )
    if user_uuid:
        tokens = await token_service.create_tokens(
            user_uuid=user_uuid, 
            response=fastapi_response, 
            agree_status=True
        )
        return tokens
    return {"error": "Authentication failed"}
