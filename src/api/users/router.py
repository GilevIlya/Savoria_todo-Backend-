from fastapi import (APIRouter, BackgroundTasks, File, Header, HTTPException,
                     Response, UploadFile)

from api.users.schemas import UserUpdateSchema
from api.users.crud import (ProfilePicNotFoundError, get_profile_pic, selecting_data_by_uuid,
                            set_profile_pic_db, update_user_data)

from api.users.service import (ProfilePictureError,
                            get_user_uuid, logout, set_prof_pic)

from db.engine import SessionDep

from authx.exceptions import JWTDecodeError

users_router = APIRouter(prefix="/users")


@users_router.get("/user_data")
async def get_dashboard_data(
    session: SessionDep, 
    authorization: str = Header(None, alias="Authorization")
):
    try:
        user_uuid = await get_user_uuid(
            auth_token=authorization
        )
        user = await selecting_data_by_uuid(uuid=user_uuid, session=session)
        result = {
            "user_data": {
                "firstname": user[0],
                "lastname": user[1],
                "email": user[2],
            }
        }
        return result
    except JWTDecodeError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except ValueError:
        raise HTTPException(status_code=401, detail="User not found")


@users_router.delete("/logout")
async def logout_user(
    response: Response
):
    await logout(
        response=response
    )


@users_router.patch("/update_data")
async def update_user_payload(
    session: SessionDep,
    new_data: UserUpdateSchema,
    authorization: str = Header(None, alias="Authorization"),
):
    update_creds = new_data.dict(exclude_unset=True)
    user_uuid = await get_user_uuid(
        auth_token=authorization
    )
    await update_user_data( 
        user_uuid=user_uuid,
        session=session, 
        new_creds=update_creds
    )
    return {"update data": "success"}


@users_router.patch("/set_avatar")
async def set_avatar_payload(
    session: SessionDep,
    background_task: BackgroundTasks,
    profile_pic: UploadFile = File(...),
    authorization: str = Header(None, alias="Authorization"),
):
    try:
        user_uuid = await get_user_uuid(
            auth_token=authorization
        )
        if profile_pic.content_type not in ["image/jpeg", "image/png"]:
            raise HTTPException(400, "Only JPG/PNG")
        picture_url = await set_prof_pic(
            user_uuid=user_uuid,
            profile_pic=profile_pic,
        )
        background_task.add_task(
            set_profile_pic_db,
            user_uuid=user_uuid,
            picture_url=picture_url,
            session=session,
        )
    except ProfilePictureError:
        raise HTTPException(status_code=500, detail="Failed to save profile picture")


@users_router.get("/get_avatar")
async def get_avatar(
    session: SessionDep, 
    authorization: str = Header(None, alias="Authorization")
):
    try:
        user_uuid = await get_user_uuid(
            auth_token=authorization
        )

        profile_pic = await get_profile_pic(
            user_uuid=user_uuid, 
            session=session
        )
        
    except ProfilePicNotFoundError:
        raise HTTPException(status_code=404, detail='Profile pic is absent')

    return {"profile_pic": profile_pic}
