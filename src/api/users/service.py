from fastapi import HTTPException, Response
from api.auth_jwt.service import security
from api.users.crud import selecting_data_by_uuid
from api.users.crud import update_user_data
from authx.exceptions import JWTDecodeError
from db.engine import SessionDep

async def decoding_token(token) -> str:
    decoded_token = security._decode_token(token)
    token_uuid = decoded_token.sub
    return token_uuid

async def return_data_for_dashboard(session: SessionDep, authorization: str):
    user_uuid = await get_user_uuid(authorization)
    user = await selecting_data_by_uuid(uuid=user_uuid, session=session)
    result = {
        "user_data": {
            "firstname": user[0],
            "lastname": user[1],
            "email": user[2],
        }
    }
    return result

async def get_user_uuid(auth_token) -> str:
    try:
        token = '' if not auth_token else auth_token.split(" ")[1]
        user_uuid = await decoding_token(token)
        return user_uuid
    except JWTDecodeError:
        raise HTTPException(status_code=401, detail='Unauthorized, token is expired')
    

async def logout(response: Response) -> None:
    try:
        response.delete_cookie(
            key='refresh_token',
            path='/'
        )
        return {'status': 'logged_out'}
    
    except:
        raise HTTPException(status_code=404)
    
async def update_user_credentials(access_token: str, session: SessionDep, new_creds: dict):
    user_uuid = await get_user_uuid(auth_token=access_token)

    await update_user_data(
            user_uuid=user_uuid,
            session=session,
            new_creds=new_creds)