from pydantic import BaseModel, EmailStr
from datetime import datetime


class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int


class TokenData(BaseModel):
    username: str | None = None


class User(BaseModel):
    username: str
    email: EmailStr | None = None
    full_name: str | None = None


class UserInDB(User):
    id: int
    password_hash: str

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    full_name: str | None = None
    password: str


class UserOut(User):
    id: int

    class Config:
        from_attributes = True


class ListBase(BaseModel):
    title: str
    description: str | None = None

    class Config:
        from_attributes = True


class ListOut(ListBase):
    id: int
    user_id: int
    todos: list["TodoOut"] | None = None

    class Config:
        from_attributes = True


class ListCreate(ListBase):
    user_id: int


class ListUpdate(ListBase):
    title: str | None = None


class ListUpdateOut(ListBase):
    id: int

    class Config:
        from_attributes = True


class TodoBase(BaseModel):
    title: str
    description: str | None = None


class TodoOut(TodoBase):
    id: int
    list_id: int
    timestamp: datetime
    is_completed: bool

    class Config:
        from_attributes = True


class TodoCreate(TodoBase):
    list_id: int


class TodoUpdate(TodoBase):
    title: str | None = None
    is_completed: bool | None = False
