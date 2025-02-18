from datetime import datetime, timedelta, timezone
import jwt
from jwt.exceptions import InvalidTokenError
from fastapi import Depends, APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from passlib.context import CryptContext

from app.core.config import settings
from app.core.database import get_db
from app.models.models import User
from app.schemas.schemas import Token, TokenData, UserCreate, UserResponse, UserInDB




router = APIRouter(tags=["Auth"])


pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(password, password_hash):
    return pwd_context.verify(password, password_hash)


def get_password_hash(password):
    return pwd_context.hash(password)


async def get_user(
    username: str, db: AsyncSession = Depends(get_db)
) -> UserInDB | None:
    query = select(User).where(User.username == username)
    result = await db.scalars(query)
    user = result.one_or_none()
    if user:
        return UserInDB.model_validate(user)
    return None


async def authenticate_user(
    username: str, password: str, db: AsyncSession = Depends(get_db)
):
    user = await get_user(username, db) 
    if not user:
        return False
    if not verify_password(password, user.password_hash):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
) -> UserResponse:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # 解码 JWT 令牌
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        username: str = payload.get(
            "sub"
        )  # "sub" 是 JWT 的标准字段，通常用于存储主体标识
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception

    user = await get_user(username=token_data.username,db=db)  # 异步操作
    if user is None:
        raise credentials_exception

    return user


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    user = await authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(seconds=settings.JWT_LIFETIME_SECONDS)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.JWT_LIFETIME_SECONDS,
    )


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register_user(
    user: UserCreate, db: AsyncSession = Depends(get_db)
) -> UserResponse:
    # 创建新用户对象
    new_user = User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        password_hash=get_password_hash(user.password),  # 加密密码
    )

    # 尝试将用户添加到数据库中
    try:
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)  # 刷新以获取完整对象（如自增 ID）
    except IntegrityError:
        # 处理用户名或邮箱的唯一性冲突
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already exists.",
        )

    return UserResponse.model_validate(new_user)  # 返回新创建的用户对象
