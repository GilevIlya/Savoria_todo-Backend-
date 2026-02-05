from redis.asyncio import Redis
from typing import List, Optional
import json


async def get_tasks_r(
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


async def set_vital_tasks_r(
    redis: Redis, 
    user_uuid: str, 
    vital_tasks: List[dict]
) -> None:
    await redis.set(f"{user_uuid}_vital_tasks", json.dumps(vital_tasks), ex=100)


async def set_tasks_r(
    redis: Redis, 
    user_uuid: str, 
    tasks_data: List[dict]
) -> None:
    await redis.set(f"{user_uuid}_tasks", json.dumps(tasks_data), ex=100)


async def delete_tasks_r(
    redis: Redis, 
    user_uuid: str
) -> None:
    await redis.delete(f"{user_uuid}_tasks")
    await redis.delete(f"{user_uuid}_vital_tasks")