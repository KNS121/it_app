from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.schemas.schemas import User, UserCreate
from app.models.models import User as DBUser
from app.database import get_db
from app.auth import get_password_hash, get_current_user

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=User)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    # Проверка на существующего пользователя
    existing_user = await db.execute(select(DBUser).where(DBUser.email == user.email))
    if existing_user.scalar():
        raise HTTPException(400, "Email уже зарегистрирован")
    
    hashed_password = get_password_hash(user.password)
    db_user = DBUser(
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name,
        is_teacher=user.is_teacher
    )
    db.add(db_user)
    await db.commit()
    return db_user

@router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user