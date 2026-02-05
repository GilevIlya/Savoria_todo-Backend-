import aiofiles
from authx.exceptions import JWTDecodeError
from fastapi import HTTPException, Response, UploadFile

from api.auth.auth_jwt.service import security
from api.users.config import PROFILE_PHOTO_UPLOAD_DIR, PROFILE_PHOTO_URL

class ProfilePictureError(Exception):
    pass

async def decoding_token(token) -> str:
    decoded_token = security._decode_token(token)
    token_uuid = decoded_token.sub
    return token_uuid


async def get_user_uuid(auth_token) -> str:
    try:
        token = "" if not auth_token else auth_token.split(" ")[1]
        user_uuid = await decoding_token(token)
        return user_uuid
    except JWTDecodeError:
        raise JWTDecodeError()


async def logout(response: Response) -> None:
    try:
        response.delete_cookie(key="refresh_token", path="/")
        return {"status": "logged_out"}

    except Exception:
        raise HTTPException(status_code=404)


async def set_prof_pic(
    user_uuid: str,
    profile_pic: UploadFile,
) -> str:
    filepath = PROFILE_PHOTO_UPLOAD_DIR / f"{user_uuid}.jpeg"
    try:
        async with aiofiles.open(filepath, mode="wb") as f:
            content = await profile_pic.read()
            await f.write(content)
        return str(PROFILE_PHOTO_URL + f"{user_uuid}.jpeg")

    except Exception as e:
        raise ProfilePictureError() from e