from fastapi import HTTPException
from src.jwt.service import security
from authx.exceptions import JWTDecodeError
from src.api.users.crud import selecting_data_by_uuid
from authx.exceptions import JWTDecodeError
from src.utils.database_engine import SessionDep

async def decoding_token(token) -> str:
    decoded_token = security._decode_token(token)
    token_uuid = decoded_token.sub
    return token_uuid

async def return_data_for_dashboard(session: SessionDep, authorization: str):
    token = '' if not authorization else authorization.split(" ")[1]
    user_uuid = await get_user_uuid(token)
    user = await selecting_data_by_uuid(uuid=user_uuid, session=session)
    result = {
        "user_data": {
            "firstname": user[0],
            "lastname": user[1],
            "email": user[2],
        }
    }
    return result

async def get_user_uuid(token) -> str:
    try:
        user_uuid = await decoding_token(token)
        return user_uuid
    except JWTDecodeError:
        raise HTTPException(status_code=401, detail='Unauthorized, token is expired')