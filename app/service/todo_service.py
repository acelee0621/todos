from app.repository.todo_repo import TodosRepository
from app.schemas.schemas import TodoResponse, TodoUpdate
from app.utils.rabbitmq import RabbitMQClient


class TodosService:
    def __init__(self, repository: TodosRepository):
        """Service layer for todos operations."""

        self.repository = repository
        self.rabbitmq = RabbitMQClient()

    async def get_todo(self, todo_id: int, current_user) -> TodoResponse:
        """Get a TodoItem by ID for the current user.

        Args:
            todo_id: The ID of the TodoItem.
            current_user (User): The current user requesting the TodoItem.

        Returns:
            TodoResponse: The TodoItem if found.
        """
        todo = await self.repository.get_by_id(todo_id, current_user)
        return TodoResponse.model_validate(todo)

    async def get_todos(
        self,
        current_user,
        list_id: int | None = None,
        status: str | None = None,
        search: str | None = None,
        order_by: str | None = None,
    ) -> list[TodoResponse]:
        """Call repository to get filtered todos."""

        todos = await self.repository.get_all(
            user_id=current_user.id,
            list_id=list_id,
            status=status,
            search=search,
            order_by=order_by,
        )

        return [TodoResponse.model_validate(todo) for todo in todos]

    async def update_todo(
        self, todo_id: int, data: TodoUpdate, current_user
    ) -> TodoResponse:
        """Update an existing TodoItem for the current user.

        Args:
            todo_id (int): The ID of the TodoItem to update.
            data (TodoUpdate): The update data containing fields to modify.
            current_user (User): The current user performing the update.

        Returns:
            TodoResponse: The updated TodoItem.
        """
        updated_todo = await self.repository.update(todo_id, data, current_user)
        if updated_todo:
            message = {
                "todo_id": updated_todo.id,
                "content": updated_todo.content,
                "priority": str(updated_todo.priority),
                "completed": updated_todo.completed,                
                "list_id": updated_todo.list_id,
                "user_id": str(updated_todo.user_id),
                "action": "updated"
            }
            await self.rabbitmq.send_message(message=message, queue="todo_notifications")
        return TodoResponse.model_validate(updated_todo)

    async def delete_todo(self, todo_id: int, current_user) -> None:
        """Delete an existing TodoItem for the current user.

        Args:
            todo_id (int): The ID of the TodoItem to delete.
            current_user (User): The current user performing the deletion.
        """
        await self.repository.delete(todo_id, current_user)
        message = {"todo_id": todo_id, "action": "deleted"}
        await self.rabbitmq.send_message(message=message, queue="todo_notifications")
