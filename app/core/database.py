import os
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.models.models import Base, User, TodoList, Todos

# 从环境变量获取数据库路径，默认为 data/db.sqlite3
database_path = os.getenv("SQLITE_DB_PATH", "data/todos.sqlite3")
SQLITE_DATABASE_URL = f"sqlite+aiosqlite:///{database_path}"


engine = create_async_engine(SQLITE_DATABASE_URL, echo=True)
SessionLocal = async_sessionmaker(
    class_=AsyncSession, expire_on_commit=False, bind=engine
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session


async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
