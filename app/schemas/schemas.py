from pydantic import BaseModel, ConfigDict, EmailStr
from datetime import datetime


class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int


class TokenData(BaseModel):
    username: str | None = None


class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: str | None = None


class UserCreate(UserBase):
    username: str
    email: EmailStr
    full_name: str | None = None
    password: str


class UserResponse(UserBase):
    id: int    

    model_config = ConfigDict(from_attributes=True)
    
    
class UserInDB(UserBase):
    id: int
    password_hash: str
    
    model_config = ConfigDict(from_attributes=True)


class TodoBase(BaseModel):
    content: str    


class TodoCreate(TodoBase):
    list_id: int


class TodoUpdate(BaseModel):  # 继承 BaseModel 避免继承 title
    content: str | None = None    
    completed: bool | None = None  # 避免默认 False


class TodoResponse(TodoBase):
    id: int
    list_id: int
    created_at: datetime
    completed: bool
    user_id: int

    model_config = ConfigDict(from_attributes=True)


class ListBase(BaseModel):
    title: str
    description: str | None = None


class ListCreate(ListBase):
    pass


class ListUpdate(BaseModel):  # 继承 BaseModel 避免继承 title
    title: str | None = None
    description: str | None = None


class ListResponse(ListBase):
    id: int
    user_id: int
    todos: list[TodoResponse] | None = None

    model_config = ConfigDict(from_attributes=True)
