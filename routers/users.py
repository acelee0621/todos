from fastapi import APIRouter, Depends
from todos.auth.auth import get_current_user, CurrentUserDep
from todos.schema.schema import UserOut


router = APIRouter(tags=["Users"], dependencies=[Depends(get_current_user)])


@router.get("/users/me", response_model=UserOut)
async def read_users_me(current_user: CurrentUserDep):
    return current_user


