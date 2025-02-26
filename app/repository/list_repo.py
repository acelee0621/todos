from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AlreadyExistsException, NotFoundException
from app.models.models import TodoList, Todos
from app.schemas.schemas import ListCreate, ListUpdate, TodoCreate


class TodoListRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: ListCreate, current_user) -> TodoList:
        """Create a new TodoList item.

        Args:
            current_user (User): current user.
            data (ListCreate): title and description of the new list.

        Returns:
            TodoList: newly created TodoList item.

        Raises:
            AlreadyExistsException: if a TodoList with the same title already exists.
        """

        new_list = TodoList(
            title=data.title, description=data.description, user_id=current_user.id
        )
        self.session.add(new_list)
        try:
            await self.session.commit()
            await self.session.refresh(new_list)
            return new_list
        except IntegrityError:
            await self.session.rollback()
            raise AlreadyExistsException(
                f"Todo list with title {data.title} already exists"
            )

    async def get_by_id(self, list_id: int, current_user) -> TodoList:
        """Get a TodoList by ID for the current user.

        Args:
            list_id: The ID of the TodoList.
            current_user_id: The ID of the current user.

        Returns:
            Optional[TodoList]: The TodoList if found, otherwise None.
        """
        query = (
            select(TodoList).where(
                TodoList.id == list_id, TodoList.user_id == current_user.id
            )
            # .options(selectinload(TodoList.todos))  #  models里定义了lazy属性就无需这条
        )
        result = await self.session.scalars(query)
        list_ = result.one_or_none()
        if not list_:
            raise NotFoundException(f"TodoList with id {list_id} not found")
        return list_

    async def get_all(self, current_user) -> list[TodoList]:
        """Get all lists.

        Returns:
            List[TodoList]: List of all todo lists.
        """
        result = await self.session.scalars(
            select(TodoList).where(TodoList.user_id == current_user.id)
            # .options(selectinload(TodoList.todos))  # 可用selectinload subqueryload
        )
        return result.all()

    async def update(self, list_id: int, data: ListUpdate, current_user) -> TodoList:
        """Update an existing TodoList item for the current user.

        Args:
            list_id (int): The ID of the TodoList to update.
            data (ListUpdate): The update data containing fields to modify.
            current_user (User): The current user performing the update.

        Returns:
            TodoList: The updated TodoList item.

        Raises:
            NotFoundException: If the TodoList is not found or does not belong to the current user.
            ValueError: If no fields are provided for update.
        """
        query = select(TodoList).where(
            TodoList.id == list_id, TodoList.user_id == current_user.id
        )
        result = await self.session.scalars(query)
        list_item = result.one_or_none()
        if not list_item:
            raise NotFoundException(
                f"TodoList with id {list_id} not found or does not belong to the current user"
            )
        update_data = data.model_dump(exclude_unset=True, exclude_none=True)
        # 确保不修改 id 和 user_id
        update_data.pop("id", None)
        update_data.pop("user_id", None)
        if not update_data:
            raise ValueError("No fields to update")
        for key, value in update_data.items():
            setattr(list_item, key, value)
        await self.session.commit()
        await self.session.refresh(list_item)
        return list_item

    async def delete(self, list_id: int, current_user) -> None:
        """Delete an existing TodoList item for the current user.

        Args:
            list_id (int): The ID of the TodoList to delete.
            current_user (User): The current user performing the deletion.

        Raises:
            NotFoundException: If the TodoList is not found or does not belong to the current user.
        """
        list = await self.session.get(TodoList, list_id)

        if not list or list.user_id != current_user.id:
            raise NotFoundException(f"TodoList with id {list_id} not found")

        await self.session.delete(list)  # 触发 ORM 级联删除
        await self.session.commit()

    async def create_todo(self, list_id: int, data: TodoCreate, current_user) -> Todos:
        """Create a new TodoItem in a specific list for the current user.

        Args:
            list_id (int): The ID of the TodoList to create the TodoItem in.
            data (TodoCreate): title and description of the new TodoItem.
            current_user (User): current user.

        Returns:
            Todos: newly created TodoItem item.

        Raises:
            AlreadyExistsException: if a TodoItem with the same title already exists.
        """

        new_todo = Todos(
            content=data.content,
            priority=data.priority,
            list_id=list_id,
            user_id=current_user.id,
        )
        self.session.add(new_todo)
        try:
            await self.session.commit()
            await self.session.refresh(new_todo)
            return new_todo
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise Exception(f"Database operation failed, create failed {e}")

    async def get_todos_by_list_id(self, list_id: int, current_user) -> list[Todos]:
        """Get all TodoItems for the current user in a specific list.

        Args:
            list_id (int): The ID of the list to retrieve TodoItems from.
            current_user (User): The current user requesting the TodoItems.

        Returns:
            list[Todos]: List of all TodoItems in the list.
        """
        query = select(Todos).where(
            Todos.list_id == list_id, Todos.user_id == current_user.id
        )
        result = await self.session.scalars(query)
        todos = result.all()
        return todos
