from typing import Annotated
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.auth.auth import get_current_user
from app.repository.todo_repo import TodosRepository
from app.service.todo_service import TodosService
from app.schemas.schemas import TodoUpdate, TodoResponse, UserResponse


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
    todo = await service.get_todo(todo_id=todo_id, current_user=current_user)
    return todo


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
    return await service.get_todos(
        current_user=current_user,
        list_id=list_id,
        status=status,
        search=search,
        order_by=order_by,
    )


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
    updated_todo = await service.update_todo(
        todo_id=todo_id, data=data, current_user=current_user
    )
    return updated_todo


@router.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    todo_id: int,
    service: TodosService = Depends(get_todos_service),
    current_user: UserResponse = Depends(get_current_user),
) -> None:
    """Delete todo."""
    await service.delete_todo(todo_id=todo_id, current_user=current_user)
