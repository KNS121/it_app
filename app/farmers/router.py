from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db_session
from app.farmers.dao import FarmerDAO
from app.farmers.rb import RBFarmer
from app.farmers.schemas import SFarmer, SFarmerAdd, SFarmerUpdDesc
from sqlalchemy.exc import IntegrityError

router = APIRouter(prefix='/farmers', tags=['Работа с фермерами'])


@router.get("/", summary="Получить всех фермеров")
async def get_all_farmers(
    request_body: RBFarmer = Depends(),
    session: AsyncSession = Depends(get_db_session)
) -> list[SFarmer]:
    return await FarmerDAO.find_all(session, **request_body.to_dict())


@router.get("/{farmer_id}", summary="Получить одного фермера по id")
async def get_farmer_by_id(
    farmer_id: int,
    session: AsyncSession = Depends(get_db_session)
) -> SFarmer | dict:
    rez = await FarmerDAO.find_full_data(session, farmer_id)
    if rez is None:
        return {'message': f'Farmer с ID {farmer_id} не найден!'}
    return rez


@router.get("/by_filter", summary="Получить одного фермера по фильтру")
async def get_farmer_by_filter(
    request_body: RBFarmer = Depends(),
    session: AsyncSession = Depends(get_db_session)
) -> SFarmer | dict:
    rez = await FarmerDAO.find_one_or_none(session, **request_body.to_dict())
    if rez is None:
        return {'message': f'Фермер с указанными вами параметрами не найден!'}
    return rez


@router.post("/add/", summary="Добавить фермера")
async def register_farmer(
    farmer: SFarmerAdd,
    session: AsyncSession = Depends(get_db_session)
) -> dict:
    try:
        await FarmerDAO.add(session, **farmer.dict())
        return {"message": "Фермер успешно добавлен!", "farmer": farmer}
    except IntegrityError as e:
        if "farmers_email_key" in str(e.orig):
            raise HTTPException(
                status_code=400,
                detail="Этот email уже используется. Пожалуйста, введите другой."
            )
        raise HTTPException(status_code=500, detail="Ошибка базы данных.")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Непредвиденная ошибка сервера.")


@router.put("/update_description/", summary='Обновить информацию о фермере')
async def update_farmer_description(
    farmer: SFarmerUpdDesc,
    session: AsyncSession = Depends(get_db_session)
) -> dict:
    update_data = farmer.dict(exclude_unset=True)
    filter_by = {
        'first_name': farmer.first_name,
        'last_name': farmer.last_name,
        'date_of_birth': farmer.date_of_birth
    }

    check = await FarmerDAO.update(session, filter_by, **update_data)
    if check:
        return {"message": "Описание фермера успешно обновлено!", "farmer": farmer}
    else:
        return {"message": "Ошибка при обновлении описания фермера!"}


@router.delete("/delete/{farmer_id}", summary='Удалить информацию о фермере')
async def delete_farmer(
    farmer_id: int,
    session: AsyncSession = Depends(get_db_session)
) -> dict:
    check = await FarmerDAO.delete(session, id=farmer_id)
    if check:
        return {"message": f"Фермер с ID {farmer_id} удален!"}
    else:
        return {"message": "Ошибка при удалении фермера!"}
