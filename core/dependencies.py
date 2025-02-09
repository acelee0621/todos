from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator
from typing import Annotated
from todos.core.database import SessionLocal


# 异步会话依赖
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session


# 使用 Annotated 标注会话依赖
DBSessionDep = Annotated[AsyncSession, Depends(get_db)]
