from fastapi import HTTPException
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import SQLAlchemyError

from todos.models.tables import List
from todos.schema.schema import ListBase, ListOut, ListUpdate, ListUpdateOut


async def create_list_in_db(db: AsyncSession, current_user, data: ListBase):
    new_list = List(
            title=data.title, description=data.description, user_id=current_user.id
        )
    db.add(new_list)
    try:        
        await db.commit()
        await db.refresh(new_list)
        return ListUpdateOut.model_validate(new_list)
    except SQLAlchemyError: 
        await db.rollback()
        raise HTTPException(status_code=500, detail="Database error, create failed")


async def get_lists(db: AsyncSession, current_user):
    try:
        result = await db.scalars(
            select(List)
            .where(List.user_id == current_user.id)
            .options(selectinload(List.todos))
        )
        lists = result.all()
        return [ListOut.model_validate(list) for list in lists]
    except SQLAlchemyError: 
        raise HTTPException(status_code=500, detail="Database error, get lists failed")


async def get_list_by_id(list_id: int, db: AsyncSession, current_user):
    try:
        query = (
            select(List)
            .where(List.id == list_id, List.user_id == current_user.id)
            .options(selectinload(List.todos))
        )
        result = await db.scalars(query)
        list_ = result.one_or_none()
        list_ = await db.get(List, list_id)
        if not list_:
            return None
        return ListOut.model_validate(list_)
    except SQLAlchemyError:         
        raise HTTPException(status_code=500, detail="Database error, get list failed")


async def update_list(list_id: int, data: ListUpdate, db: AsyncSession, current_user):
    try:
        query = select(List).where(List.id == list_id, List.user_id == current_user.id)
        result = await db.scalars(query)
        list_item = result.one_or_none()
        if not list_item:
            return None
        # 动态更新字段，排除不可修改的字段
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            # 确保不修改 id 和 user_id
            if key not in {"id", "user_id"}:
                setattr(list_item, key, value)
        db.add(list_item)
        await db.commit()
        await db.refresh(list_item)
        return ListUpdateOut.model_validate(list_item)
    except SQLAlchemyError:  
        await db.rollback()
        raise HTTPException(status_code=500, detail="Database error, update failed")


async def delete_list(list_id: int, db: AsyncSession, current_user):
    try:
        query = select(List).where(List.id == list_id, List.user_id == current_user.id)
        result = await db.scalars(query)
        list_item = result.one_or_none()

        if not list_item:
            return None  # 返回 None 由路由函数处理 404

        await db.delete(list_item)
        await db.commit()
        return list_item  # 返回被删除的对象
    except SQLAlchemyError:  # 仅捕获 SQL 相关异常，避免不必要的 broad exception
        await db.rollback()
        raise HTTPException(status_code=500, detail="Database error, delete failed")