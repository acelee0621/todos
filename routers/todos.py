from fastapi import APIRouter, Depends, HTTPException, status
from todos.auth.auth import get_current_user, CurrentUserDep
from todos.core.dependencies import DBSessionDep
from todos.schema.schema import TodoCreate, TodoOut, TodoUpdate
from todos.crud.todos import (
    create_todo_item,
    delete_todo,
    get_todos,
    get_todos_in_list,
    get_todo,
    update_todo,
)


router = APIRouter(tags=["Todos"], dependencies=[Depends(get_current_user)])


@router.post("/todos", response_model=TodoOut, status_code=status.HTTP_201_CREATED)
async def create_todo(current_user: CurrentUserDep, db: DBSessionDep, data: TodoCreate):
    created_todo = await create_todo_item(data=data, db=db, current_user=current_user)
    return created_todo


@router.get("/todos", response_model=list[TodoOut])
async def get_all_todos(current_user: CurrentUserDep, db: DBSessionDep):
    all_todos = await get_todos(db=db, current_user=current_user)
    if not all_todos:
        raise HTTPException(status_code=404, detail="Items not found")
    return all_todos


@router.get("/todos/list/{list_id}", response_model=list[TodoOut])
async def get_todos_by_list_id(
    list_id: int, db: DBSessionDep, current_user: CurrentUserDep
):
    todos = await get_todos_in_list(list_id=list_id, db=db, current_user=current_user)
    if not todos:
        raise HTTPException(status_code=404, detail="Items not found")
    return todos


@router.get("/todos/{todo_id}", response_model=TodoOut)
async def get_todo_by_id(todo_id: int, db: DBSessionDep, current_user: CurrentUserDep):
    todo = await get_todo(todo_id=todo_id, db=db, current_user=current_user)
    if not todo:
        raise HTTPException(status_code=404, detail="Item not found")
    return todo


@router.put("/todos/{todo_id}", response_model=TodoOut, status_code=status.HTTP_200_OK)
async def update_todo_endpoint(
    todo_id: int, data: TodoUpdate, db: DBSessionDep, current_user: CurrentUserDep
):
    updated_todo = await update_todo(
        todo_id=todo_id, data=data, db=db, current_user=current_user
    )
    if not updated_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return updated_todo


@router.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo_endpoint(
    todo_id: int, db: DBSessionDep, current_user: CurrentUserDep
):
    result = await delete_todo(todo_id=todo_id, db=db, current_user=current_user)
    if not result:
        raise HTTPException(status_code=404, detail="Item not found")
    return
