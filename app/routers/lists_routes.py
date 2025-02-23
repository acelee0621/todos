from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.logging import get_logger
from app.core.security import get_current_user
from app.repository.list_repo import TodoListRepository
from app.service.list_service import TodoListService
from app.schemas.schemas import ListCreate, ListUpdate, ListResponse, TodoCreate, TodoResponse, UserResponse


# Set up logger for this module
logger = get_logger(__name__)


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
    try:
        created_list = await service.create_list(data=data, current_user=current_user)
        logger.info(f"Created list {created_list.id}")
        return created_list
    except Exception as e:
        logger.error(f"Failed to create list: {str(e)}")
        raise


@router.get("/lists/{list_id}", response_model=ListResponse)
async def get_list(
    list_id: int,
    service: TodoListService = Depends(get_list_service),
    current_user: UserResponse = Depends(get_current_user),
) -> ListResponse:
    """Get list by id."""
    try:
        list_ = await service.get_list(list_id=list_id, current_user=current_user)
        logger.info(f"Retrieved list {list_id}")
        return list_
    except Exception as e:
        logger.error(f"Failed to get list {list_id}: {str(e)}")
        raise


@router.get("/lists", response_model=list[ListResponse])
async def get_all_lists(
    service: TodoListService = Depends(get_list_service),
    current_user: UserResponse = Depends(get_current_user),
):
    """Get all lists."""
    try:
        all_list = await service.get_lists(current_user=current_user)
        logger.info(f"Retrieved {len(all_list)} lists")
        return all_list
    except Exception as e:
        logger.error(f"Failed to fetch all lists: {str(e)}")
        raise


@router.post("/lists/{list_id}/todos", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
async def create_todo(
    list_id: int,
    data: TodoCreate,
    service: TodoListService = Depends(get_list_service),
    current_user: UserResponse = Depends(get_current_user),
)->TodoResponse:
    """Create new todo in a specific list."""
    try:
        created_todo = await service.create_todo(list_id=list_id, data=data, current_user=current_user)
        logger.info(f"Created todo item {created_todo.id} in list {list_id}")
        return created_todo
    except Exception as e:
        logger.error(f"Failed to create todo item in list {list_id}: {str(e)}")
        raise


@router.get("/lists/{list_id}/todos", response_model=list[TodoResponse])
async def get_todos_by_list_id(
    list_id: int,
    service: TodoListService = Depends(get_list_service),
    current_user: UserResponse = Depends(get_current_user),
)->list[TodoResponse]:
    """Get all todos in specific list."""
    try:
        todos = await service.get_todos_in_list(list_id=list_id, current_user=current_user)
        logger.info(f"Retrieved {len(todos)} todos from list {list_id}")    
        return todos
    except Exception as e:
        logger.error(f"Failed to fetch todos from list {list_id}: {str(e)}")
        raise


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
    try:
        updated_list = await service.update_list(
            list_id=list_id, data=data, current_user=current_user
        )
        logger.info(f"Updated list {list_id}")
        return updated_list
    except Exception as e:
        logger.error(f"Failed to update list {list_id}: {str(e)}")
        raise


@router.delete("/lists/{list_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_list(
    list_id: int,
    service: TodoListService = Depends(get_list_service),
    current_user: UserResponse = Depends(get_current_user),
) -> None:
    """Delete list."""
    try:
        await service.delete_list(list_id=list_id, current_user=current_user)
        logger.info(f"Deleted list {list_id}")
    except Exception as e:
        logger.error(f"Failed to delete list {list_id}: {str(e)}")
        raise
