from models.base import engine
from models.tables import Base, User, List, Todo
import asyncio

print("Creating database ....")


# 异步表创建
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# 运行初始化函数
asyncio.run(init_db())

print("Database created!")
