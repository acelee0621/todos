from app.repository.list_repo import TodoListRepository
from app.schemas.schemas import ListResponse, ListCreate, ListUpdate, TodoCreate, TodoResponse


class TodoListService:
        
    def __init__(self, repository: TodoListRepository):
        """Service layer for list operations."""
        
        self.repository = repository        
        
    async def create_list(self, data: ListCreate, current_user) -> ListResponse:
        """Create a new TodoList item.
        
        Args:
            data (ListCreate): title and description of the new list.
            current_user (User): current user.
        
        Returns:
            ListResponse: newly created TodoList item.
        """

        new_list = await self.repository.create(data, current_user)
        return ListResponse.model_validate(new_list)        
        
    async def get_list(self, list_id: int, current_user) -> ListResponse:
        """Get a TodoList by ID for the current user.
        
        Args:
            list_id: The ID of the TodoList.
            current_user (User): current user.
        
        Returns:
            ListResponse: The TodoList if found, otherwise None.
        """
        list = await self.repository.get_by_id(list_id, current_user)
        return ListResponse.model_validate(list)    

    async def get_lists(self, current_user) -> list[ListResponse]:
        """Get all lists for the current user.
        
        Args:
            current_user (User): current user.
        
        Returns:
            list[ListResponse]: List of all todo lists.
        """
        lists = await self.repository.get_all(current_user)
        return [ListResponse.model_validate(list) for list in lists]

    async def update_list(self, list_id: int, data: ListUpdate, current_user) -> ListResponse:
        """Update an existing TodoList item for the current user.
        
        Args:
            list_id: The ID of the TodoList to update.
            data (ListUpdate): The update data containing fields to modify.
            current_user (User): current user.
        
        Returns:
            ListResponse: The updated TodoList item.
        """
        list = await self.repository.update(list_id, data, current_user)
        return ListResponse.model_validate(list)

    async def delete_list(self, list_id: int, current_user) -> None:
        """Delete an existing TodoList item for the current user.

        Args:
            list_id (int): The ID of the TodoList to delete.
            current_user (User): The current user performing the deletion.
        
        """

        await self.repository.delete(list_id, current_user)
        
        
    async def create_todo(self, list_id: int, data: TodoCreate, current_user) -> TodoResponse:
        """Create a new TodoItem in a specific list for the current user.

        Args:
            list_id (int): The ID of the TodoList to create the TodoItem in.
            data (TodoCreate): title and description of the new TodoItem.
            current_user (User): current user.

        Returns:
            TodoResponse: newly created TodoItem item.
        """
        todo = await self.repository.create_todo(list_id,data, current_user)
        return TodoResponse.model_validate(todo)
    
    
    async def get_todos_in_list(self, list_id: int, current_user) -> list[TodoResponse]:
        """Get all TodoItems in a given list for the current user.

        Args:
            list_id: The ID of the list to retrieve TodoItems from.
            current_user (User): The current user requesting the TodoItems.

        Returns:
            list[TodoResponse]: List of all TodoItems in the list.
        """
        todos = await self.repository.get_todos_by_list_id(list_id, current_user)
        return [TodoResponse.model_validate(todo) for todo in todos]