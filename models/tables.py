from typing import Optional
from sqlalchemy import String, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase
from datetime import datetime, timezone


# 基础类
class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(
        String(64), index=True, unique=True, nullable=False
    )
    email: Mapped[str] = mapped_column(
        String(120), index=True, unique=True, nullable=False
    )
    password_hash: Mapped[Optional[str]] = mapped_column(String(256))
    full_name: Mapped[Optional[str]] = mapped_column(String(64))

    # 一对多关系：User -> List
    lists: Mapped[list["List"]] = relationship(
        "List", back_populates="owner", cascade="all, delete-orphan"
    )
    # 一对多关系：User -> Todo
    todos: Mapped[list["Todo"]] = relationship(
        "Todo", back_populates="owner", cascade="all, delete-orphan"
    )


class List(Base):
    __tablename__ = "lists"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(
        String(64), default="Default List", index=True, nullable=False
    )
    description: Mapped[Optional[str]] = mapped_column(Text)

    # 外键：关联到 User 表
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    # 多对一关系：List -> User
    owner: Mapped["User"] = relationship("User", back_populates="lists")

    # 一对多关系：List -> Todo
    todos: Mapped[list["Todo"]] = relationship(
        "Todo", back_populates="list", cascade="all, delete-orphan"
    )

    # 表级约束：确保每个用户的列表标题唯一
    __table_args__ = (
        UniqueConstraint("title", "user_id", name="unique_list_per_user"),
    )


class Todo(Base):
    __tablename__ = "todos"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(64), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    timestamp: Mapped[datetime] = mapped_column(
        index=True, default=lambda: datetime.now(timezone.utc)
    )
    is_completed: Mapped[bool] = mapped_column(
        default=False, index=True, nullable=False
    )
    # 外键：关联到 List 表
    list_id: Mapped[int] = mapped_column(ForeignKey("lists.id"), nullable=False)
    # 外键：关联到 User 表
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    # 多对一关系：Todo -> List
    list: Mapped["List"] = relationship("List", back_populates="todos")
    # 多对一关系：Todo -> User
    owner: Mapped["User"] = relationship("User", back_populates="todos")
