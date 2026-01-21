from time import perf_counter
from typing import Optional

from redis.asyncio import Redis
from sqlalchemy.exc import SQLAlchemyError


from fastapi import APIRouter, Header, UploadFile, Depends, File, HTTPException, BackgroundTasks, Query

from db.engine import SessionDep
from redis_utils.client import get_redis
from api.users.tasks.schemas import TaskCreate, TaskEdit
from api.users.service import get_user_uuid
from api.users.tasks.crud import (create_task_in_db, select_all_tasks,
                                  edit_task_data, replace_task_to_completed,
                                  search_tasks_by_name, select_vital_tasks,
                                  delete_task_db)

from api.users.tasks.service import (
    set_task_pic, serialize_tasks, exclude_unset,
    get_tasks, set_tasks,
    get_vital_tasks_r, set_vital_tasks,
    delete_tasks_r)


users_tasks_router = APIRouter(prefix='/users/tasks')

@users_tasks_router.post("/create_task")
async def create_task(
    background_tasks: BackgroundTasks,
    session: SessionDep,
    authorization: str = Header(None, alias="Authorization"),
    task_data: TaskCreate = Depends(TaskCreate.get_tasks_fields),
    task_img: UploadFile | None = File(None),
    redis_client: Redis = Depends(get_redis),
):
    user_uuid = await get_user_uuid(
        auth_token=authorization)

    background_tasks.add_task(
        delete_tasks_r,
        redis=redis_client,
        user_uuid=user_uuid)

    task_id = await create_task_in_db(
        session=session, user_uuid=user_uuid,
        task_data=dict(task_data))
    if task_img:
        if task_img.content_type not in ["image/jpeg", "image/png"]:
            raise HTTPException(400, "Only JPG/PNG")
        await set_task_pic(
            task_img=task_img,
            task_id=task_id,
            user_uuid=user_uuid
        )

@users_tasks_router.get("/get_all_tasks")
async def get_all_tasks(
    session: SessionDep,
    background_tasks: BackgroundTasks,
    authorization: str = Header(None, alias="Authorization"),
    redis_client: Redis = Depends(get_redis),
):
    user_uuid = await get_user_uuid(
        auth_token=authorization)
    tasks_from_cache = await get_tasks(
        redis=redis_client,
        user_uuid=user_uuid)
    if tasks_from_cache:
        return tasks_from_cache

    tasks_from_db = await select_all_tasks(
        session=session,
        user_uuid=user_uuid)
    tasks_data = await serialize_tasks(
        tasks=tasks_from_db, user_uuid=user_uuid)

    background_tasks.add_task(
        set_tasks,
        redis=redis_client,
        user_uuid=user_uuid,
        tasks_data=tasks_data)
    return tasks_data

@users_tasks_router.get("/get_vital_tasks")
async def get_vital_tasks(
        background_tasks: BackgroundTasks,
        session: SessionDep,
        authorization: str = Header(None, alias="Authorization"),
        redis_client: Redis = Depends(get_redis),
):
    now = perf_counter()
    user_uuid = await get_user_uuid(
        auth_token=authorization
    )
    vital_tasks = await get_vital_tasks_r(
        redis=redis_client,
        user_uuid=user_uuid
    )
    if vital_tasks:
        return vital_tasks

    db_vital_tasks = await select_vital_tasks(
        session=session,
        user_uuid=user_uuid
    )
    vital_tasks_data = await serialize_tasks(
        tasks=db_vital_tasks,
        user_uuid=user_uuid
    )

    background_tasks.add_task(
        set_vital_tasks,
        redis=redis_client,
        user_uuid=user_uuid,
        vital_tasks=vital_tasks_data
    )
    return vital_tasks_data


@users_tasks_router.patch("/edit_task/{task_id}")
async def edit_task(
        background_task: BackgroundTasks,
        session: SessionDep,
        task_id: int,
        task_data: TaskEdit = Depends(TaskEdit.get_optional_tasks_fields),
        task_img: UploadFile | None = File(None),
        authorization: str = Header(None, alias="Authorization"),
        redis_client: Redis = Depends(get_redis)
):
    user_uuid = await get_user_uuid(
        auth_token=authorization)

    list_of_changes = await exclude_unset(
        task_data=task_data)
    try:
        await edit_task_data(
                session=session,
                user_uuid=user_uuid,
                task_id=task_id,
                task_data=list_of_changes)
        if task_img:
            if task_img.content_type not in ["image/jpeg", "image/png"]:
                raise HTTPException(400, "Only JPG/PNG")
            await set_task_pic(
                task_img=task_img,
                task_id=task_id,
                user_uuid=user_uuid)
        background_task.add_task(
                delete_tasks_r,
                redis=redis_client, user_uuid=user_uuid)
    except ValueError:
        raise HTTPException(status_code=404, detail="No such task")
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="DataBase Error")
    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))


@users_tasks_router.patch("/complete_task/{task_id}")
async def complete_task(
        background_tasks: BackgroundTasks,
        session: SessionDep,
        task_id: int,
        authorization: str = Header(None, alias="Authorization"),
        redis_client: Redis = Depends(get_redis)
):
    user_uuid = await get_user_uuid(
        auth_token=authorization
    )
    try:
        await replace_task_to_completed(
            session=session,
            user_uuid=user_uuid,
            task_id=task_id
        )

        background_tasks.add_task(
            delete_tasks_r,
            redis=redis_client, user_uuid=user_uuid
        )

    except ValueError:
        raise HTTPException(status_code=404, detail="Task not found")
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="DataBase Error")

@users_tasks_router.get("/search")
async def search_tasks(
        session: SessionDep,
        task_name: Optional[str] = Query(None, description="Текст поиска"),
        authorization: str = Header(None, alias="Authorization")
):
    if not task_name:
        return {

        }
    user_uuid = await get_user_uuid(
        auth_token=authorization
    )
    try:
        found_tasks = await search_tasks_by_name(
            session=session,
            user_uuid=user_uuid,
            task_name=task_name
        )
        if found_tasks is None:
            return {

            }
        serialized_tasks = await serialize_tasks(
            tasks=found_tasks,
            user_uuid=user_uuid
        )
        return serialized_tasks
    except ValueError:
        raise HTTPException(status_code=404, detail="Task Error")
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="DataBase Error")

@users_tasks_router.delete("/delete_task/{task_id}")
async def delete_task(
        background_task: BackgroundTasks,
        task_id: int,
        session: SessionDep,
        authorization: str = Header(None, alias="Authorization"),
        redis_client: Redis = Depends(get_redis)
):
    user_uuid = await get_user_uuid(
        auth_token=authorization
    )
    try:
        await delete_task_db(
            session=session,
            task_id=task_id,
            user_uuid=user_uuid
        )

        background_task.add_task(
            delete_tasks_r,
            redis=redis_client,
            user_uuid=user_uuid
        )
    except ValueError:
        raise HTTPException(status_code=404, detail="Task Error")