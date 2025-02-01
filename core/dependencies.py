from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator
from typing import Annotated
from todos.models.base import SessionLocal


# 异步会话依赖
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session


# 使用 Annotated 标注会话依赖
SessionDep = Annotated[AsyncSession, Depends(get_db)]
