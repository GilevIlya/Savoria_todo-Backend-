from datetime import timedelta
from uuid import UUID

from authx import AuthX, AuthXConfig
from authx.exceptions import JWTDecodeError
from fastapi import HTTPException, Request, Response

from api.auth.auth_jwt.config import jwt_auth_config

config = AuthXConfig()
config.JWT_SECRET_KEY = jwt_auth_config.JWT_SECRET_KEY
config.JWT_ACCESS_COOKIE_NAME = "access_token"
config.JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=10)
config.JWT_REFRESH_COOKIE_NAME = "refresh_token"
config.JWT_TOKEN_LOCATION = ["headers"]
config.JWT_COOKIE_SECURE = False
config.JWT_COOKIE_SAMESITE = "lax"
config.JWT_COOKIE_CSRF_PROTECT = False
config.JWT_COOKIE_DOMAIN = None

security = AuthX(config=config)


class JwtTokenService:
    def __init__(self, authx_config: AuthX):
        self.config = authx_config

    async def create_tokens(
        self, 
        user_uuid: UUID, 
        response: Response, 
        agree_status: bool
    ) -> dict:
        jwt_access_token = self.config.create_access_token(
            uid=str(user_uuid), 
            expiry=timedelta(minutes=10)
        )
        jwt_refresh_token = self.config.create_refresh_token(
            uid=str(user_uuid), 
            expiry=timedelta(days=20)
        )

        await self.create_cookie(
            jwt_refresh_token=jwt_refresh_token,
            response=response,
            agree_status=agree_status,
        )
        return {
            "access_token": jwt_access_token,
            "expires_in": "900",
            "token_type": "Bearer",
        }

    async def generate_access_token(
        self, 
        user_uuid: str
    ) -> str:
        jwt_access_token = self.config.create_access_token(
            uid=str(user_uuid), 
            expiry=timedelta(minutes=10)
        )
        return jwt_access_token

    async def create_cookie(
        self, 
        jwt_refresh_token: str, 
        response: Response, 
        agree_status: bool
    ) -> None:
        self.config.set_refresh_cookies(
            jwt_refresh_token,
            response,
            max_age=1728000 if agree_status is True else None,
        )


async def get_uuid_from_cookie(
    request: Request
) -> str:
    try:
        refresh_token = request.cookies.get("refresh_token")
        if not refresh_token:
            raise HTTPException(
                status_code=401, detail="Invalid cookie or absent, redirect to sign_up"
            )
        uuid = security._decode_token(refresh_token.encode()).sub
        return uuid
    except JWTDecodeError:
        raise HTTPException(status_code=401, detail="Invalid cookie or absent, redirect to sign_up")


token_service = JwtTokenService(authx_config=security)


def get_jwt_token_service_obj() -> JwtTokenService:
    return token_service
