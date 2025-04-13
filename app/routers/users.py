from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
#from app.schemas.schemas import (UserCreate,
from app.schemas.schemas import UserResponse  # Изменены импорты
from app.models.models import User as DBUser
from app.database import get_db
from app.auth import get_password_hash, get_current_active_user

router = APIRouter(prefix="/users", tags=["users"])

# @router.post("/", response_model=UserResponse)
# async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
#     # Проверка существующего пользователя
#     existing_user = await db.execute(
#         select(DBUser).where(DBUser.email == user.email)
#     if existing_user.scalar():
#         raise HTTPException(400, "Email already registered")
#
#     # Создание пользователя с учетом новой структуры
#     db_user = DBUser(
#         email=user.email,
#         first_name=user.first_name,
#         last_name=user.last_name,
#         patronymic=user.patronymic,
#         hashed_password=get_password_hash(user.password),
#         role=user.role,
#         is_active=True  # Автоматически активируем пользователя
#     )
#
#     db.add(db_user)
#     await db.commit()
#     await db.refresh(db_user)
#     return db_user

@router.get("/me", response_model=UserResponse)
async def read_users_me(
    current_user: UserResponse = Depends(get_current_active_user)
):
    return current_user