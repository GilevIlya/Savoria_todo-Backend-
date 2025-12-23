from authx import AuthX, AuthXConfig
from fastapi import Response, Request, HTTPException
from datetime import timedelta
from src.jwt.config import jwt_auth_config
from authx.exceptions import JWTDecodeError


config = AuthXConfig()
config.JWT_SECRET_KEY = jwt_auth_config.JWT_SECRET_KEY
config.JWT_ACCESS_COOKIE_NAME = "access_token"
config.JWT_ACCESS_TOKEN_EXPIRES=timedelta(seconds=10)
config.JWT_REFRESH_COOKIE_NAME = "refresh_token"
config.JWT_TOKEN_LOCATION = ["headers"]
config.JWT_COOKIE_SECURE = False
config.JWT_COOKIE_SAMESITE = "lax"
config.JWT_COOKIE_CSRF_PROTECT = False
config.JWT_COOKIE_DOMAIN = None

security = AuthX(config=config)

async def create_tokens(user_uuid, response, agree_status):
    jwt_access_token = security.create_access_token(uid=str(user_uuid), expiry=timedelta(seconds=10))
    jwt_refresh_token = security.create_refresh_token(uid=str(user_uuid), expiry=timedelta(days=20))
    await create_cookie(jwt_refresh_token, response, agree_status=agree_status)
    return {
            'access_token': jwt_access_token,
            'expires_in': '900',
            'token_type': 'Bearer',
        }

async def create_only_access_token(uuid):
    jwt_access_token = security.create_access_token(uid=str(uuid), expiry=timedelta(seconds=10))
    return jwt_access_token

async def create_cookie(jwt_refresh_token, response: Response, agree_status):
    security.set_refresh_cookies(jwt_refresh_token, 
                                 response, 
                                 max_age=1728000 if agree_status is True else None,)
    
async def uuid_from_cookie(request: Request):
    try:
        refresh_token = request.cookies.get('refresh_token')
        if not refresh_token:
            raise HTTPException(status_code=401, detail='Invalid cookie or absent, redirect to sign_up')
        uuid = security._decode_token(refresh_token.encode()).sub
        return uuid
    except JWTDecodeError:
        raise HTTPException(status_code=401, detail='Invalid cookie or absent, redirect to sign_up')