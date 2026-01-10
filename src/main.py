import uvicorn
import time

from fastapi import FastAPI
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles
from api.auth.router import auth_router
from db.engine import create_user_table
from api.users.router import users_router
from api.users.tasks.router import users_tasks_router
from redis_utils.client import init_redis, close_redis

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"

@asynccontextmanager
async def lifespan(app: FastAPI):
    redis = await init_redis()
    app.state.redis = redis
    try:
        yield
    finally:
        await close_redis(redis)

app = FastAPI(
    lifespan=lifespan
)
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(users_tasks_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount(
    "/uploads",
    StaticFiles(directory=UPLOAD_DIR),
    name="uploads"
)

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True, host="0.0.0.0")