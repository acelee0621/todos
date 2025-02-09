import sys

from fastapi import FastAPI, Response, status
from fastapi import __version__ as fastapi_version
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from todos.core.config import settings
from todos.auth import auth
from todos.routers import users, lists, todos
from todos.core.database import create_db_and_tables



@asynccontextmanager
async def lifespan(app: FastAPI):    
    await create_db_and_tables()
    yield
    


app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,    
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(lists.router)
app.include_router(todos.router)


@app.get("/server-status", include_in_schema=False)
async def health_check(response: Response, token: str | None = None):
    if token == "Ace":
        response.status_code = 200
        data = {
            "status": "ok 👍 ",
            "FastAPI Version": fastapi_version,
            "Python Version": sys.version_info,
        }
        return data
    else:
        response.status_code = status.HTTP_404_NOT_FOUND  # 404
        return {"detail": "Not Found ❌"}
