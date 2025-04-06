from fastapi import Request, HTTPException, status, Depends
from jose import jwt, JWTError
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy import select

from app.config import get_auth_data
from app.database import get_db_session
from app.exceptions import TokenExpiredException, NoJwtException, NoUserIdException, ForbiddenException
from app.users.auth import create_access_token
from app.users.dao import UsersDAO
from app.users.models import User, UserRoles


def get_token(request: Request, token_type: str):
    if token_type == 'access':
        token = request.cookies.get('users_access_token')
    elif token_type == 'refresh':
        token = request.cookies.get('users_refresh_token')
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid token type requested')

    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f'{token_type.capitalize()} token not found')

    return token


async def refresh_access_token(
    request: Request,
    session: AsyncSession = Depends(get_db_session)
):
    token = get_token(request, 'refresh')
    try:
        auth_data = get_auth_data()
        payload = jwt.decode(token, auth_data['secret_key'], algorithms=[auth_data['algorithm']])
    except JWTError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f'Invalid refresh token: {str(e)}')

    expire = payload.get('exp')
    if not expire or datetime.fromtimestamp(int(expire), tz=timezone.utc) < datetime.now(timezone.utc):
        raise TokenExpiredException(detail='Refresh token expired')

    user_id = payload.get('sub')
    if not user_id:
        raise NoUserIdException(detail='No user ID in token')

    user = await UsersDAO.find_one_or_none_by_id(session, int(user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User not found')

    new_access_token = create_access_token({"sub": str(user.id)})
    return {"access_token": new_access_token}


async def get_current_user(
    request: Request,
    session: AsyncSession = Depends(get_db_session)
) -> User:
    token = get_token(request, 'access')
    try:
        auth_data = get_auth_data()
        payload = jwt.decode(token, auth_data['secret_key'], algorithms=[auth_data['algorithm']])
    except JWTError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f'Invalid access token: {str(e)}')

    expire = payload.get('exp')
    if not expire or datetime.fromtimestamp(int(expire), tz=timezone.utc) < datetime.now(timezone.utc):
        raise TokenExpiredException(detail='Access token expired')

    user_id = payload.get('sub')
    if not user_id:
        raise NoUserIdException(detail='No user ID in token')

    # Загрузка пользователя с жадной загрузкой его ролей
    query = select(User).options(selectinload(User.roles)).where(User.id == int(user_id))
    result = await session.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User not found')

    return user


async def get_current_admin_user(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
) -> User:
    query = select(User).options(
        joinedload(User.roles).joinedload(UserRoles.role)
    ).where(User.id == current_user.id)
    result = await session.execute(query)
    user = result.unique().scalar_one_or_none()

    if not user or not user.is_admin:
        raise HTTPException(status_code=403, detail="Access denied")

    return user


async def get_current_farmer_user(
        current_user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_db_session)
) -> User:
    query = (
        select(User)
        .options(selectinload(User.roles).selectinload(UserRoles.role))
        .where(User.id == current_user.id)
    )
    result = await session.execute(query)
    user = result.scalars().first()

    if not user or not any(role.role.name == 'farmer' for role in user.roles):
        raise HTTPException(status_code=403, detail="Access denied")

    return user
