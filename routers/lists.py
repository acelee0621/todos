from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from auth.auth import get_current_user
from core.database import get_db
from schemas.schemas import ListCreate, ListUpdate, ListResponse, UserResponse
from crud.lists import (
    get_lists,
    create_list_in_db,
    get_list_by_id,
    update_list,
    delete_list,
)


router = APIRouter(tags=["Lists"], dependencies=[Depends(get_current_user)])


@router.post("/lists", response_model=ListResponse, status_code=status.HTTP_201_CREATED)
async def create_list(
    data: ListCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
) -> ListResponse:
    created_list = await create_list_in_db(data=data, db=db, current_user=current_user)
    return created_list


@router.get("/lists", response_model=list[ListResponse])
async def get_all_lists(
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
) -> list[ListResponse]:
    all_list = await get_lists(db=db, current_user=current_user)
    if not all_list:
        raise HTTPException(status_code=404, detail="Lists not found")
    return all_list


@router.get("/lists/{list_id}", response_model=ListResponse)
async def get_list(
    list_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
) -> ListResponse:
    list_ = await get_list_by_id(list_id=list_id, db=db, current_user=current_user)
    if not list_:
        raise HTTPException(status_code=404, detail="List not found")
    return list_


@router.patch(
    "/lists/{list_id}", response_model=ListResponse, status_code=status.HTTP_200_OK
)
async def update_list_endpoint(
    list_id: int,
    data: ListUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
) -> ListResponse:
    updated_list = await update_list(
        list_id=list_id, data=data, db=db, current_user=current_user
    )
    if not updated_list:
        raise HTTPException(status_code=404, detail="List not found")
    return updated_list


@router.delete("/lists/{list_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_list_endpoint(
    list_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
) -> None:
    result = await delete_list(list_id=list_id, db=db, current_user=current_user)

    if not result:
        raise HTTPException(status_code=404, detail="Item not found")

    return  # 204 响应不返回内容
