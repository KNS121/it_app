from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Union

from app.database import get_db_session
from app.users.dependencies import get_current_farmer_user
from app.users.models import User

from app.fields.dao import FieldsDAO
from app.fields.schemas import (
    SFieldCreate,
    SFieldResponse,
    SFieldUpdate,
    SFieldFilter
)

router = APIRouter(prefix='/fields', tags=['Работа с полями'])


# @router.post(
#     "/",
#     response_model=SFieldResponse,
#     status_code=status.HTTP_201_CREATED,
#     summary="Добавить новое поле"
# )
# async def create_field(
#     field_data: SFieldCreate,
#     session: AsyncSession = Depends(get_db_session),
#     current_user: User = Depends(get_current_farmer_user)
# ):
#     """
#     Создание нового поля с автоматическим расчетом площади.
#     Требует роли фермера.
#     """
#     try:
#         field_data_dict = field_data.model_dump()
#         field_data_dict['farmer_id'] = current_user.id
#         new_field = await FieldsDAO.create_field(session, field_data_dict)
#         return new_field
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=f"Ошибка создания поля: {str(e)}"
#         )

@router.post(
    "/",
    response_model=SFieldResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_field(
        field_data: SFieldCreate,
        session: AsyncSession = Depends(get_db_session),
        current_user: User = Depends(get_current_farmer_user)
):
    try:
        field_dict = field_data.model_dump()
        geometry = field_dict.pop("geometry")  # Извлекаем WKT из экстра данных

        field_dict.update({
            "farmer_id": current_user.id,
            "geometry": geometry
        })

        new_field = await FieldsDAO.add_field(session, field_dict)
        return new_field
    except Exception as e:
        raise HTTPException(400, detail=str(e))


@router.get(
    "/",
    response_model=List[SFieldResponse],
    summary="Получить все поля"
)
async def get_all_fields(
    session: AsyncSession = Depends(get_db_session)
):
    """Получение списка всех полей с геоданными"""
    return await FieldsDAO.find_fields(session)


@router.get(
    "/my",
    response_model=List[SFieldResponse],
    summary="Получить мои поля"
)
async def get_my_fields(
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_farmer_user)
):
    """Получение полей текущего фермера"""
    return await FieldsDAO.get_by_farmer(session, current_user.id)


@router.get(
    "/{field_id}",
    response_model=SFieldResponse,
    summary="Получить поле по ID"
)
async def get_field_by_id(
    field_id: int,
    session: AsyncSession = Depends(get_db_session)
):
    """Получение детальной информации о поле по ID"""
    field = await FieldsDAO.find_full_data(session, field_id)
    if not field:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Поле с ID {field_id} не найдено"
        )
    return field


@router.get(
    "/by_filter/",
    response_model=List[SFieldResponse],
    summary="Фильтрация полей"
)
async def filter_fields(
    filter_params: SFieldFilter = Depends(),
    session: AsyncSession = Depends(get_db_session)
):
    """Фильтрация полей по параметрам"""
    try:
        return await FieldsDAO.find_fields(
            session,
            **filter_params.model_dump(exclude_none=True)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put(
    "/{field_id}",
    response_model=SFieldResponse,
    summary="Обновить информацию о поле"
)
async def update_field(
    field_id: int,
    update_data: SFieldUpdate,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_farmer_user)
):
    """Обновление информации о поле (только для владельца)"""
    # Проверка прав собственности
    field = await FieldsDAO.find_full_data(session, field_id)
    if not field or field['farmer_id'] != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет прав для изменения этого поля"
        )

    try:
        updated_field = await FieldsDAO.update_field(
            session,
            field_id,
            update_data.model_dump(exclude_unset=True)
        )
        return updated_field
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete(
    "/{field_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить поле"
)
async def delete_field(
    field_id: int,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_farmer_user)
):
    """Удаление поля (только для владельца)"""
    # Проверка прав собственности
    field = await FieldsDAO.find_full_data(session, field_id)
    if not field or field['farmer_id'] != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет прав для удаления этого поля"
        )

    success = await FieldsDAO.delete_field_by_id(session, field_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Поле не найдено"
        )
