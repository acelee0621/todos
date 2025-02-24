from uuid import UUID

from sqlalchemy import select, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.models.models import Todos
from app.schemas.schemas import TodoUpdate


class TodosRepository:
    """Repository for handling Todos database operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, todo_id: int, current_user) -> Todos:
        """Get a TodoItem by ID for the current user.

        Args:
            list_id (int): The ID of the TodoItem to retrieve.
            current_user (User): The current user requesting the TodoItem.

        Returns:
            Todos: The TodoItem if found.

        Raises:
            NotFoundException: If the TodoItem is not found or does not belong to the current user.
        """

        query = select(Todos).where(
            Todos.id == todo_id, Todos.user_id == current_user.id
        )
        result = await self.session.scalars(query)
        todo = result.one_or_none()
        if not todo:
            raise NotFoundException(f"TodoItem with id {todo_id} not found")
        return todo

    async def get_all(
        self,
        user_id: UUID,
        list_id: int | None = None,
        status: str | None = None,
        search: str | None = None,
        order_by: str | None = None,
    ) -> list[Todos]:
        """Get todos based on filters."""

        query = select(Todos).where(Todos.user_id == user_id)

        if list_id:
            query = query.where(Todos.list_id == list_id)

        if status:
            if status == "finished":
                query = query.where(Todos.completed.is_(True))
            elif status == "unfinished":
                query = query.where(Todos.completed.is_(False))

        if search:
            query = query.where(Todos.content.ilike(f"%{search}%"))

        if order_by:
            if order_by == "created_at desc":
                query = query.order_by(desc(Todos.created_at))
            elif order_by == "created_at asc":
                query = query.order_by(asc(Todos.created_at))
            elif order_by == "priority desc":
                query = query.order_by(desc(Todos.priority))
            elif order_by == "priority asc":
                query = query.order_by(asc(Todos.priority))

        result = await self.session.scalars(query)
        return result.all()

    async def update(self, todo_id: int, data: TodoUpdate, current_user) -> Todos:
        """Update an existing TodoItem item for the current user.

        Args:
            list_id (int): The ID of the TodoItem to update.
            data (TodoUpdate): The update data containing fields to modify.
            current_user (User): The current user performing the update.

        Returns:
            Todos: The updated TodoItem item.

        Raises:
            ValueError: If no fields are provided for update.
            NotFoundException: If the TodoItem is not found or does not belong to the current user.
        """
        query = select(Todos).where(
            Todos.id == todo_id, Todos.user_id == current_user.id
        )
        result = await self.session.scalars(query)
        todo_item = result.one_or_none()
        if not todo_item:
            raise NotFoundException(
                f"TodoItem with id {todo_id} not found or does not belong to the current user or list"
            )
        update_data = data.model_dump(exclude_unset=True, exclude_none=True)
        # 确保不修改 list_id 和 user_id
        update_data.pop("list_id", None)
        update_data.pop("user_id", None)
        if not update_data:
            raise ValueError("No fields to update")
        # 动态更新字段
        for key, value in update_data.items():
            setattr(todo_item, key, value)
        await self.session.commit()
        await self.session.refresh(todo_item)
        return todo_item

    async def delete(self, todo_id: int, current_user) -> None:
        """Delete an existing TodoItem for the current user.

        Args:
            list_id (int): The ID of the TodoItem to delete.
            current_user (User): The current user performing the deletion.

        Raises:
            NotFoundException: If the TodoItem is not found or does not belong to the current user.
        """
        query = select(Todos).where(
            Todos.id == todo_id, Todos.user_id == current_user.id
        )
        result = await self.session.scalars(query)
        todo_item = result.one_or_none()
        if not todo_item:
            raise NotFoundException(f"TodoItem with id {todo_id} not found")
        await self.session.delete(todo_item)
        await self.session.commit()
