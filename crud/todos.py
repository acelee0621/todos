from fastapi import HTTPException
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from todos.models.tables import Todo
from todos.schema.schema import TodoCreate, TodoOut, TodoUpdate


async def create_todo_item(db: AsyncSession, data: TodoCreate, current_user):
    new_todo = Todo(
        title=data.title,
        description=data.description,
        list_id=data.list_id,
        user_id=current_user.id,
    )
    db.add(new_todo)
    try:
        await db.commit()
        await db.refresh(new_todo)
        return TodoOut.model_validate(new_todo)
    except SQLAlchemyError:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Database error, create failed")


async def get_todos(db: AsyncSession, current_user):
    try:
        query = select(Todo).where(Todo.user_id == current_user.id)
        result = await db.scalars(query)
        todos = result.all()
        return [TodoOut.model_validate(todo) for todo in todos]
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error, get todos failed")


async def get_todos_in_list(list_id: int, db: AsyncSession, current_user):
    try:
        query = select(Todo).where(Todo.list_id == list_id, Todo.user_id == current_user.id)
        result = await db.scalars(query)
        todos = result.all()
        return [TodoOut.model_validate(todo) for todo in todos]
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error, get todos failed")


async def get_todo(todo_id: int, db: AsyncSession, current_user):
    try:
        query = select(Todo).where(Todo.id == todo_id, Todo.user_id == current_user.id)
        result = await db.scalars(query)
        todo = result.one_or_none()
        if not todo:
            return None
        return TodoOut.model_validate(todo)
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error, get todo failed")


async def update_todo(todo_id: int, data: TodoUpdate, db: AsyncSession, current_user):
    try:
        query = select(Todo).where(Todo.id == todo_id, Todo.user_id == current_user.id)
        result = await db.scalars(query)
        todo_item = result.one_or_none()
        if not todo_item:
            return None
        # 动态更新字段，排除不可修改的字段
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            # 确保不修改 list_id 和 user_id
            if key not in {"list_id", "user_id"}:
                setattr(todo_item, key, value)
        db.add(todo_item)
        await db.commit()
        await db.refresh(todo_item)
        return TodoOut.model_validate(todo_item)
    except SQLAlchemyError:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Database error, update failed")


async def delete_todo(todo_id: int, db: AsyncSession, current_user):
    try:
        query = select(Todo).where(Todo.id == todo_id, Todo.user_id == current_user.id)
        result = await db.scalars(query)
        todo_item = result.one_or_none()
        if not todo_item:
            return None  # 返回 None 表示未找到待删除的项
        await db.delete(todo_item)
        await db.commit()  # 提交事务
        return todo_item  # 返回被删除的对象
    except SQLAlchemyError:
        await db.rollback()  # 回滚事务
        raise HTTPException(status_code=500, detail="Database error, delete failed")

