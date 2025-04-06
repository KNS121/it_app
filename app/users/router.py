import logging

from fastapi import APIRouter, HTTPException, status, Response, Depends, Request
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db_session
from app.users.auth import get_password_hash, authenticate_user, create_access_token, create_refresh_token
from app.users.dao import UsersDAO
from app.users.dependencies import get_current_user, get_current_admin_user, refresh_access_token
from app.users.models import User
from app.users.schemas import SUserRegister, SUserAuth

router = APIRouter(prefix='/auth', tags=['Аутентификация'])


@router.post("/register/", summary="Зарегистрировать пользователя")
async def register_user(
        user_data: SUserRegister,
        session: AsyncSession = Depends(get_db_session)
) -> dict:
    logging.info(f"Полученные данные: {user_data}")
    try:
        # Используем model_validate вместо прямого создания экземпляра
        validated_data = SUserRegister.model_validate(user_data.model_dump())
    except ValidationError as e:
        raise HTTPException(
            status_code=422,
            detail=e.errors()
        )

    # Проверка существующего пользователя
    existing_user = await UsersDAO.find_one_or_none(session, email=validated_data.email)
    if existing_user:
        raise HTTPException(status_code=409, detail="Пользователь уже существует")

    # Хеширование пароля
    hashed_password = get_password_hash(validated_data.password)

    # Создание пользователя
    new_user = await UsersDAO.add(
        session,
        email=validated_data.email,
        password=hashed_password,
        phone_number=validated_data.phone_number,
        first_name=validated_data.first_name,
        last_name=validated_data.last_name
    )

    return {"message": "Регистрация успешна!"}


@router.post("/login/", summary="Аутентифицировать пользователя")
async def auth_user(
    response: Response,
    user_data: SUserAuth,
    session: AsyncSession = Depends(get_db_session)
):
    check = await authenticate_user(session, email=user_data.email, password=user_data.password)
    if check is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Неверная почта или пароль')

    access_token = create_access_token({"sub": str(check.id)})
    refresh_token = create_refresh_token({"sub": str(check.id)})

    response.set_cookie(key="users_access_token", value=access_token, httponly=True)
    response.set_cookie(key="users_refresh_token", value=refresh_token, httponly=True)

    return {'ok': True, 'access_token': access_token, 'refresh_token': refresh_token, 'message': 'Авторизация успешна!'}


@router.post("/refresh-token/", summary="Обновить access токен")
async def refresh_access_token_route(
    request: Request,
    response: Response,
    session: AsyncSession = Depends(get_db_session)
):
    token_data = await refresh_access_token(request, session)
    new_access_token = token_data["access_token"]

    response.set_cookie(key="users_access_token", value=new_access_token, httponly=True)

    return {"access_token": new_access_token}


@router.post("/logout/", summary="Разлогинить пользователя")
async def logout_user(response: Response):
    response.delete_cookie(key="users_access_token")
    response.delete_cookie(key="users_refresh_token")
    return {'message': 'Пользователь успешно вышел из системы'}


@router.get("/me/", summary="Получить информацию о текущем пользователе", tags=["Защищённый ресурс"])
async def get_me(
    user_data: User = Depends(get_current_user)
):
    return user_data


@router.get("/all_users/", summary="Получить информацию о всех пользователях")
async def get_all_users(
    session: AsyncSession = Depends(get_db_session),
    user_data: User = Depends(get_current_admin_user)
):
    return await UsersDAO.find_all(session)


@router.post("/roles/", summary="Добавить новую роль")
async def create_role(
    role_name: str,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    try:
        new_role = await UsersDAO.create_role(session, role_name=role_name)
        return {"message": "Роль успешно создана", "роль": new_role}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/roles/{role_id}", summary="Удалить роль")
async def delete_role(
    role_id: int,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_admin_user)
):
    try:
        return await UsersDAO.delete_role(session, role_id=role_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{user_id}/roles", summary="Назначить роль пользователю")
async def update_user_role(
    user_id: int,
    role_name: str,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    try:
        return await UsersDAO.assign_role_to_user(session, user_id=user_id, role_name=role_name)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
