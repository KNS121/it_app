# app/routers/users.py
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.schemas.schemas import UserCreate, UserResponse
from app.models.models import User as DBUser
from app.database import get_db
from app.auth import get_password_hash, get_current_active_user

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    # Проверка существующего email
    existing_user = await db.execute(
        select(DBUser).where(DBUser.email == user.email)
    )
    if existing_user.scalar():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email уже зарегистрирован"
        )

    # Создание нового пользователя
    db_user = DBUser(
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        patronymic=user.patronymic,
        hashed_password=get_password_hash(user.password),
        role=user.role,
        is_active=True
    )

    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    return db_user


@router.get("/me", response_model=UserResponse)
async def read_users_me(
        current_user: UserResponse = Depends(get_current_active_user)
):
    return current_user