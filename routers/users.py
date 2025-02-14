from fastapi import APIRouter, Depends
from todos.auth.auth import get_current_user
from todos.schemas.schemas import UserResponse


router = APIRouter(tags=["Users"], dependencies=[Depends(get_current_user)])


@router.get("/users/me", response_model=UserResponse)
async def read_users_me(current_user: UserResponse = Depends(get_current_user)):
    return current_user


