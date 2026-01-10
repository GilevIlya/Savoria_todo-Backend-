from api.users.tasks.config import TASK_UPLOAD_DIR
from typing import List
from db.models import TasksTable
from fastapi import HTTPException

TASK_IMG_URL = "http://localhost:8000/uploads/task_images/"

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
            "status": task.status,
            "priority": task.priority,
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