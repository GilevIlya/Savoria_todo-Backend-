from api.users.tasks.config import TASK_UPLOAD_DIR, TASK_IMG_URL
from typing import List, Optional
from db.models import TasksTable
from fastapi import HTTPException
from redis.asyncio import Redis

import json
import aiofiles

async def set_task_pic(
        task_img,
        task_id: int,
        user_uuid: str
    ) -> None:
    filepath = (TASK_UPLOAD_DIR / f"{task_id}_{user_uuid}.jpeg")
    try:
        async with aiofiles.open(filepath, mode="wb") as f:
            content = await task_img.read()
            await f.write(content)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(f'{e}, picture installing error'))

async def serialize_tasks(
        tasks: List[TasksTable],
        user_uuid: str) -> List[dict]:
    serialized_tasks = [
        {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "status": task.status.value ,
            "priority": task.priority.value,
            "deadline": task.deadline,
            "task_img": TASK_IMG_URL+f"{task.id}_{user_uuid}.jpeg",
        }
        for task in tasks
    ]
    return serialized_tasks

async def exclude_unset(task_data) -> dict:
     return {
        key: value for key, value in dict(task_data).items() if value is not None
    }

async def get_tasks(
        redis: Redis,
        user_uuid: str,
) -> Optional[List[dict]]:
    result = await redis.get(f"{user_uuid}_tasks")
    return json.loads(result) if result else None

async def get_vital_tasks_r(
        redis: Redis,
        user_uuid: str,
) -> Optional[List[dict]]:
    result = await redis.get(f"{user_uuid}_vital_tasks")
    return json.loads(result) if result else None

async def set_vital_tasks(
        redis: Redis,
        user_uuid: str,
        vital_tasks: List[dict]
):
    await redis.set(f"{user_uuid}_vital_tasks", json.dumps(vital_tasks), ex=100)

async def set_tasks(
        redis: Redis,
        user_uuid: str,
        tasks_data: List[dict]
):
    await redis.set(f"{user_uuid}_tasks", json.dumps(tasks_data), ex=100)

async def delete_tasks_r(
        redis: Redis,
        user_uuid: str
):
    await redis.delete(f"{user_uuid}_tasks")
    await redis.delete(f"{user_uuid}_vital_tasks")

async def serialize_TaskTable_obj_data(
        task_obj: TasksTable
):
    return {
                'id': task_obj.id,
                'user_id': task_obj.user_id,
                'title': task_obj.title,
                'description': task_obj.description,
                'priority': str(task_obj.priority.value),
                'deadline': task_obj.deadline,
                'created_at': task_obj.created_at,
                'updated_at': task_obj.updated_at
            }