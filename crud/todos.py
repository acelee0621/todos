from todos.models.tables import Todo
from todos.schema.schema import TodoCreate, TodoOut, TodoUpdate
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession


async def create_todo_item(db: AsyncSession, data: TodoCreate, current_user):
    new_todo = Todo(
        title=data.title,
        description=data.description,
        list_id=data.list_id,
        user_id=current_user.id,
    )
    db.add(new_todo)
    await db.commit()
    await db.refresh(new_todo)
    return TodoOut.model_validate(new_todo)


async def get_todos(db: AsyncSession, current_user):
    query = select(Todo).where(Todo.user_id == current_user.id)
    result = await db.scalars(query)
    todos = result.all()
    return [TodoOut.model_validate(todo) for todo in todos]


async def get_todos_in_list(list_id: int, db: AsyncSession, current_user):
    query = select(Todo).where(Todo.list_id == list_id, Todo.user_id == current_user.id)
    result = await db.scalars(query)
    todos = result.all()
    return [TodoOut.model_validate(todo) for todo in todos]


async def get_todo(todo_id: int, db: AsyncSession, current_user):
    query = select(Todo).where(Todo.id == todo_id, Todo.user_id == current_user.id)
    result = await db.scalars(query)
    todo = result.one_or_none()
    if not todo:
        return None
    return TodoOut.model_validate(todo)


async def update_todo(todo_id: int, data: TodoUpdate, db: AsyncSession, current_user):
    query = select(Todo).where(Todo.id == todo_id, Todo.user_id == current_user.id)
    result = await db.scalars(query)
    todo = result.one_or_none()
    if not todo:
        return None
    # 动态更新字段，排除不可修改的字段
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        # 确保不修改 list_id 和 user_id
        if key not in {"list_id", "user_id"}:
            setattr(todo, key, value)
    db.add(todo)
    await db.commit()
    await db.refresh(todo)
    return TodoOut.model_validate(todo)


async def delete_todo(todo_id: int, db: AsyncSession, current_user):
    try:
        query = select(Todo).where(Todo.id == todo_id, Todo.user_id == current_user.id)
        result = await db.scalars(query)
        todo = result.one_or_none()
        if not todo:
            return None  # 返回 None 表示未找到待删除的项
        await db.delete(todo)
        await db.commit()  # 提交事务
        return todo  # 返回被删除的对象
    except Exception as e:
        await db.rollback()  # 回滚事务
        raise e  # 抛出异常，由路由函数处理
