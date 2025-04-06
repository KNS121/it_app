from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_auth_data
from app.users.dao import UsersDAO

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=15)  # Access токен истекает через 15 минут
    to_encode.update({"exp": expire})
    auth_data = get_auth_data()
    return jwt.encode(to_encode, auth_data['secret_key'], algorithm=auth_data['algorithm'])


def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=30)  # Refresh токен истекает через 30 дней
    to_encode.update({"exp": expire})
    auth_data = get_auth_data()
    return jwt.encode(to_encode, auth_data['secret_key'], algorithm=auth_data['algorithm'])


async def authenticate_user(session: AsyncSession, email: EmailStr, password: str):
    user = await UsersDAO.find_one_or_none(session, email=email)
    if not user or not verify_password(plain_password=password, hashed_password=user.password):
        return None
    return user


def verify_refresh_token(token: str):
    try:
        auth_data = get_auth_data()
        payload = jwt.decode(token, auth_data['secret_key'], algorithms=[auth_data['algorithm']])
        return payload
    except JWTError:
        return None
