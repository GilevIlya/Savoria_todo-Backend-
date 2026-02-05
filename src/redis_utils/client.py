from fastapi import Request
from redis.asyncio import Redis

from redis_utils.config import redis_config


async def init_redis() -> Redis:
    redis = Redis.from_url(
        redis_config.REDIS_URL, encoding="utf-8", decode_responses=True
    )

    return redis


async def close_redis(redis: Redis):
    redis.close()


def get_redis(request: Request) -> Redis:
    return request.app.state.redis
