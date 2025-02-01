from fastapi import APIRouter, Depends, HTTPException
from todos.auth.auth import get_current_user, CurrentUser
from todos.core.dependencies import SessionDep
from todos.schema.schema import ListOut, ListBase, ListUpdate, ListUpdateOut
from todos.crud.lists import (
    get_lists,
    create_list_in_db,
    get_list_by_id,
    update_list,
    delete_list,
)


router = APIRouter(tags=["Lists"], dependencies=[Depends(get_current_user)])


@router.post("/lists", response_model=ListUpdateOut)
async def create_list(*, current_user: CurrentUser, db: SessionDep, data: ListBase):
    created_list = await create_list_in_db(data=data, db=db, current_user=current_user)
    return created_list


@router.get("/lists", response_model=list[ListOut])
async def get_all_lists(current_user: CurrentUser, db: SessionDep):
    all_list = await get_lists(db=db, current_user=current_user)
    if not all_list:
        raise HTTPException(status_code=404, detail="Lists not found")
    return all_list


@router.get("/lists/{list_id}", response_model=ListOut)
async def get_list(
    list_id: int,
    db: SessionDep,
    current_user: CurrentUser,
):
    list_ = await get_list_by_id(list_id=list_id, db=db, current_user=current_user)
    if not list_:
        raise HTTPException(status_code=404, detail="List not found")
    return list_


@router.put("/lists/{list_id}", response_model=ListUpdateOut)
async def update_list_endpoint(
    list_id: int, data: ListUpdate, db: SessionDep, current_user: CurrentUser
):
    updated_todo = await update_list(
        list_id=list_id, data=data, db=db, current_user=current_user
    )
    if not updated_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return updated_todo


@router.delete("/lists/{list_id}")
async def delete_list_endpoint(list_id: int, db: SessionDep, current_user: CurrentUser):
    try:
        result = await delete_list(list_id=list_id, db=db, current_user=current_user)
        if not result:
            raise HTTPException(status_code=404, detail="Item not found")
        return {"message": "Item deleted successfully"}
    except Exception:
        # 捕获所有异常并返回 500 错误
        raise HTTPException(status_code=500, detail="Internal server error")
