from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.auth.auth import get_current_user
from app.repository.list_repo import TodoListRepository
from app.service.list_service import TodoListService
from app.schemas.schemas import ListCreate, ListUpdate, ListResponse, TodoCreate, TodoResponse, UserResponse


router = APIRouter(tags=["Lists"], dependencies=[Depends(get_current_user)])


def get_list_service(session: AsyncSession = Depends(get_db)) -> TodoListService:
    """Dependency for getting list service instance."""
    repository = TodoListRepository(session)
    return TodoListService(repository)


@router.post("/lists", response_model=ListResponse, status_code=status.HTTP_201_CREATED)
async def create_list(
    data: ListCreate,
    service: TodoListService = Depends(get_list_service),
    current_user: UserResponse = Depends(get_current_user),
) -> ListResponse:
    """Create new list."""
    created_list = await service.create_list(data=data, current_user=current_user)
    return created_list


@router.get("/lists/{list_id}", response_model=ListResponse)
async def get_list(
    list_id: int,
    service: TodoListService = Depends(get_list_service),
    current_user: UserResponse = Depends(get_current_user),
) -> ListResponse:
    """Get list by id."""
    list_ = await service.get_list(list_id=list_id, current_user=current_user)
    return list_


@router.get("/lists", response_model=list[ListResponse])
async def get_all_lists(
    service: TodoListService = Depends(get_list_service),
    current_user: UserResponse = Depends(get_current_user),
):
    """Get all lists."""
    all_list = await service.get_lists(current_user=current_user)
    return all_list


@router.post("/lists/{list_id}/todos", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
async def create_todo(
    list_id: int,
    data: TodoCreate,
    service: TodoListService = Depends(get_list_service),
    current_user: UserResponse = Depends(get_current_user),
)->TodoResponse:
    """Create new todo in a specific list."""
    created_todo = await service.create_todo(list_id=list_id, data=data, current_user=current_user)
    return created_todo


@router.get("/lists/{list_id}/todos", response_model=list[TodoResponse])
async def get_todos_by_list_id(
    list_id: int,
    service: TodoListService = Depends(get_list_service),
    current_user: UserResponse = Depends(get_current_user),
)->list[TodoResponse]:
    """Get all todos in specific list."""
    todos = await service.get_todos_in_list(list_id=list_id, current_user=current_user)    
    return todos


@router.patch(
    "/lists/{list_id}", response_model=ListResponse, status_code=status.HTTP_200_OK
)
async def update_list(
    list_id: int,
    data: ListUpdate,
    service: TodoListService = Depends(get_list_service),
    current_user: UserResponse = Depends(get_current_user),
) -> ListResponse:
    """Update list."""
    updated_list = await service.update_list(
        list_id=list_id, data=data, current_user=current_user
    )
    return updated_list


@router.delete("/lists/{list_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_list(
    list_id: int,
    service: TodoListService = Depends(get_list_service),
    current_user: UserResponse = Depends(get_current_user),
) -> None:
    """Delete list."""
    await service.delete_list(list_id=list_id, current_user=current_user)
