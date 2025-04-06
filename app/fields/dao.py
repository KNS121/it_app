from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy.future import select
from fastapi import HTTPException
from geoalchemy2.functions import ST_AsGeoJSON
import json

from app.dao.base import BaseDAO
from app.fields.models import Field
from app.farmers.models import Farmer


class FieldsDAO(BaseDAO):
    model = Field

    @classmethod
    async def find_fields(cls, session: AsyncSession, **filter_params):
        """Получить поля с фильтрацией и преобразованием геометрии в GeoJSON"""
        query = (
            select(cls.model)
            .options(joinedload(cls.model.farmer))
            .filter_by(**filter_params)
        )

        result = await session.execute(query)
        fields = result.scalars().all()

        fields_data = []
        for field in fields:
            # Конвертируем геометрию в GeoJSON
            geom_json = await session.scalar(
                select(ST_AsGeoJSON(field.geometry))
            )

            field_dict = {
                "id": field.id,
                "name": field.name,
                "coordinates": json.loads(geom_json)['coordinates'][0],  # Извлекаем координаты полигона
                "area_hectares": field.area_hectares,
                "crop_rotation": field.crop_rotation,
                "cultivation_technology": field.cultivation_technology,
                "farmer_id": field.farmer_id,
                "farmer": field.farmer.last_name if field.farmer else None
            }
            fields_data.append(field_dict)

        return fields_data

    @classmethod
    async def find_full_data(cls, session: AsyncSession, field_id: int):
        """Получить полную информацию о поле с геометрией"""
        query = (
            select(cls.model)
            .options(joinedload(cls.model.farmer))
            .where(cls.model.id == field_id)
        )

        result = await session.execute(query)
        field = result.scalar_one_or_none()

        if not field:
            raise HTTPException(status_code=404, detail="Field not found")

        # Конвертация геометрии
        geom_json = await session.scalar(
            select(ST_AsGeoJSON(field.geometry))
        )

        return {
            "id": field.id,
            "name": field.name,
            "geometry": json.loads(geom_json),
            "area_hectares": field.area_hectares,
            "crop_rotation": field.crop_rotation,
            "cultivation_technology": field.cultivation_technology,
            "farmer_id": field.farmer_id,
            "farmer": field.farmer.last_name
        }

    @classmethod
    async def add_field(cls, session: AsyncSession, field_data: dict):
        """Создать новое поле с валидацией геометрии"""
        try:
            # Проверка и преобразование координат
            if 'geometry' not in field_data:
                raise ValueError("Geometry is required")

            new_field = cls.model(**field_data)
            session.add(new_field)
            await session.commit()
            await session.refresh(new_field)
            return new_field

        except Exception as e:
            await session.rollback()
            raise HTTPException(
                status_code=400,
                detail=f"Error creating field: {str(e)}"
            )

    @classmethod
    async def update_field(cls, session: AsyncSession, field_id: int, update_data: dict):
        """Обновить поле с обработкой геометрии"""
        try:
            field = await session.get(cls.model, field_id)
            if not field:
                return {"error": "Field not found"}

            # Обновление геометрии при необходимости
            if 'geometry' in update_data:
                field.geometry = update_data['geometry']
                del update_data['geometry']

            for key, value in update_data.items():
                setattr(field, key, value)

            await session.commit()
            return {"success": "Field updated successfully"}

        except Exception as e:
            await session.rollback()
            return {"error": str(e)}

    @classmethod
    async def delete_field_by_id(cls, session: AsyncSession, field_id: int):
        """Удалить поле по ID"""
        field = await session.get(cls.model, field_id)
        if not field:
            return False

        await session.delete(field)
        await session.commit()
        return True

    @classmethod
    async def get_by_farmer(cls, session: AsyncSession, farmer_id: int):
        """Получить все поля фермера"""
        result = await session.execute(
            select(cls.model)
            .where(cls.model.farmer_id == farmer_id)
        )
        return result.scalars().all()
