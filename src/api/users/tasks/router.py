from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from fastapi import APIRouter, Header, UploadFile, Depends, File

from db.engine import SessionDep
from api.users.tasks.schemas import TaskCreate, TaskEdit
from api.users.service import get_user_uuid
from api.users.tasks.crud import create_task_in_db, select_all_tasks, edit_task_data
from api.users.tasks.service import set_task_pic, serialize_tasks, exclude_unset

users_tasks_router = APIRouter(prefix='/users/tasks')

@users_tasks_router.post("/create_task")
async def create_task(
    session: SessionDep,
    authorization: str = Header(None, alias="Authorization"),
    task_data: TaskCreate = Depends(TaskCreate.get_tasks_fields),
    task_img: UploadFile | None = File(None),
):
    user_uuid = await get_user_uuid(auth_token=authorization)
    task_id = await create_task_in_db(
        session=session, user_uuid=user_uuid,
        task_data=dict(task_data))
    if task_img:
        await set_task_pic(
            task_img=task_img,
            task_id=task_id,
            user_uuid=user_uuid
        )

@users_tasks_router.get("/get_all_tasks")
async def get_all_tasks(
    session: SessionDep,
    authorization: str = Header(None, alias="Authorization"),
):
    user_uuid = await get_user_uuid(auth_token=authorization)
    tasks_from_db = await select_all_tasks(
        session=session,
        user_uuid=user_uuid)
    tasks_data = await serialize_tasks(
        tasks=tasks_from_db, user_uuid=user_uuid)
    return tasks_data

@users_tasks_router.patch("/edit_task/{task_id}")
async def edit_task(
        session: SessionDep,
        task_id: int,
        task_data: TaskEdit = Depends(TaskEdit.get_optional_tasks_fields),
        task_img: UploadFile | None = File(None),
        authorization: str = Header(None, alias="Authorization"),
):
    user_uuid = await get_user_uuid(auth_token=authorization)
    list_of_changes = await exclude_unset(task_data=task_data)
    try:
        await edit_task_data(
                session=session,
                user_uuid=user_uuid,
                task_id=task_id,
                task_data=list_of_changes)
        if task_img:
            await set_task_pic(
                     task_img=task_img,
                     task_id=task_id,
                     user_uuid=user_uuid
                 )
    except ValueError:
        raise HTTPException(status_code=404, detail="No such task")
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="DataBase Error")
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))