import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.auth.router import auth_router
from src.utils.create_tables import create_user_table
from src.api.users.router import users_router

app = FastAPI()
app.include_router(auth_router)
app.include_router(users_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def on_startup():
    await create_user_table()

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True, host="0.0.0.0")