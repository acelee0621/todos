from todos.models.tables import List
from todos.schema.schema import ListBase, ListOut, ListUpdate, ListUpdateOut
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


async def create_list_in_db(db: AsyncSession, current_user, data: ListBase):
    new_list = List(
        title=data.title, description=data.description, user_id=current_user.id
    )
    db.add(new_list)
    await db.commit()
    await db.refresh(new_list)
    return ListUpdateOut.model_validate(new_list)


async def get_lists(db: AsyncSession, current_user):
    print(current_user)
    result = await db.scalars(
        select(List)
        .where(List.user_id == current_user.id)
        .options(selectinload(List.todos))
    )
    lists = result.all()
    return [ListOut.model_validate(list) for list in lists]


async def get_list_by_id(list_id: int, db: AsyncSession, current_user):
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


async def update_list(list_id: int, data: ListUpdate, db: AsyncSession, current_user):
    query = select(List).where(List.id == list_id, List.user_id == current_user.id)
    result = await db.scalars(query)
    list = result.one_or_none()
    if not list:
        return None
    # 动态更新字段，排除不可修改的字段
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        # 确保不修改 id 和 user_id
        if key not in {"id", "user_id"}:
            setattr(list, key, value)
    db.add(list)
    await db.commit()
    await db.refresh(list)
    return ListUpdateOut.model_validate(list)


async def delete_list(list_id: int, db: AsyncSession, current_user):
    try:
        query = select(List).where(List.id == list_id, List.user_id == current_user.id)
        result = await db.scalars(query)
        list = result.one_or_none()
        if not list:
            return None  # 返回 None 表示未找到待删除的项
        await db.delete(list)
        await db.commit()  # 提交事务
        return list  # 返回被删除的对象
    except Exception as e:
        await db.rollback()  # 回滚事务
        raise e  # 抛出异常，由路由函数处理
