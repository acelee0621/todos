from typing import Annotated
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.logging import get_logger
from app.core.security import get_current_user
from app.repository.todo_repo import TodosRepository
from app.service.todo_service import TodosService
from app.schemas.schemas import TodoUpdate, TodoResponse, UserResponse


# Set up logger for this module
logger = get_logger(__name__)


router = APIRouter(tags=["Todos"], dependencies=[Depends(get_current_user)])


def get_todos_service(session: AsyncSession = Depends(get_db)) -> TodosService:
    """Dependency for getting todos service instance."""
    repository = TodosRepository(session)
    return TodosService(repository)


@router.get("/todos/{todo_id}", response_model=TodoResponse)
async def get_todo_by_id(
    todo_id: int,
    service: TodosService = Depends(get_todos_service),
    current_user: UserResponse = Depends(get_current_user),
) -> TodoResponse:
    """Get todo by id."""
    try:
        todo = await service.get_todo(todo_id=todo_id, current_user=current_user)
        logger.info(f"Retrieved todo item {todo_id}")
        return todo
    except Exception as e:
        logger.error(f"Failed to fetch todo item {todo_id}: {str(e)}")
        raise


@router.get("/todos", response_model=list[TodoResponse])
async def get_all_todos(
    list_id: Annotated[int | None, Query(description="Filter by list ID")] = None,
    status: Annotated[
        str | None, Query(description="Filter by status (unfinished/finished)")
    ] = None,
    search: Annotated[
        str | None, Query(description="Search todos by title or description")
    ] = None,
    order_by: Annotated[
        str | None, Query(description="Order by field (e.g., created_at desc/asc)")
    ] = None,
    service: TodosService = Depends(get_todos_service),
    current_user: UserResponse = Depends(get_current_user),
) -> list[TodoResponse]:
    """
    Get all todos with optional filtering and sorting.
    """
    try:
        result = await service.get_todos(
            current_user=current_user,
            list_id=list_id,
            status=status,
            search=search,
            order_by=order_by,
        )
        logger.info(f"Retrieved {len(result)} todo items")
        return result
    except Exception as e:
        logger.error(f"Failed to fetch todo items: {str(e)}")
        raise


@router.patch(
    "/todos/{todo_id}", response_model=TodoResponse, status_code=status.HTTP_200_OK
)
async def update_todo(
    todo_id: int,
    data: TodoUpdate,
    service: TodosService = Depends(get_todos_service),
    current_user: UserResponse = Depends(get_current_user),
) -> TodoResponse:
    """Update todo."""
    try:
        updated_todo = await service.update_todo(
            todo_id=todo_id, data=data, current_user=current_user
        )
        logger.info(f"Updated todo item {todo_id}")
        return updated_todo
    except Exception as e:
        logger.error(f"Failed to update todo item {todo_id}: {str(e)}")
        raise


@router.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    todo_id: int,
    service: TodosService = Depends(get_todos_service),
    current_user: UserResponse = Depends(get_current_user),
) -> None:
    """Delete todo."""
    try:
        await service.delete_todo(todo_id=todo_id, current_user=current_user)
        logger.info(f"Deleted todo item {todo_id}")
    except Exception as e:
        logger.error(f"Failed to delete todo item {todo_id}: {str(e)}")
        raise
