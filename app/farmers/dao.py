from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy.future import select
from fastapi import HTTPException

from app.dao.base import BaseDAO
from app.farmers.models import Farmer


class FarmerDAO(BaseDAO):
    model = Farmer

    @classmethod
    async def find_full_data(cls, session: AsyncSession, farmer_id: int):
        query = select(cls.model).options(joinedload(cls.model.fields)).filter_by(id=farmer_id)
        result = await session.execute(query)
        farmer_info = result.unique().scalar_one_or_none()
        if not farmer_info:
            raise HTTPException(status_code=404, detail="Farmer not found")
        return farmer_info.to_dict()