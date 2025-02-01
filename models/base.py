from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

SQLITE_DATABASE_URL = "sqlite+aiosqlite:///./database.db"

engine = create_async_engine(
    SQLITE_DATABASE_URL, echo=True, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(class_=AsyncSession, expire_on_commit=False, bind=engine)
