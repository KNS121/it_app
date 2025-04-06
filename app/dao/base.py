from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException


class BaseDAO:
    model = None

    @classmethod
    async def find_all(cls, session: AsyncSession, **filter_by):
        query = select(cls.model)
        if filter_by:
            query = query.filter_by(**filter_by)
        result = await session.execute(query)
        return result.scalars().all()

    @classmethod
    async def find_one_or_none_by_id(cls, session: AsyncSession, data_id: int):
        result = await session.execute(select(cls.model).filter_by(id=data_id))
        entity = result.scalar_one_or_none()
        if not entity:
            raise HTTPException(status_code=404, detail="Entity not found")
        return entity

    @classmethod
    async def find_one_or_none(cls, session: AsyncSession, **filter_by):
        result = await session.execute(select(cls.model).filter_by(**filter_by))
        return result.scalar_one_or_none()

    @classmethod
    async def add(cls, session: AsyncSession, **values):
        new_instance = cls.model(**values)
        session.add(new_instance)
        try:
            await session.commit()
        except SQLAlchemyError as e:
            await session.rollback()
            raise HTTPException(status_code=400, detail=str(e))
        return new_instance

    @classmethod
    async def update(cls, session: AsyncSession, entity, **values):
        for key, value in values.items():
            setattr(entity, key, value)
        session.add(entity)
        await session.commit()
        return entity

    @classmethod
    async def delete(cls, session: AsyncSession, entity):
        await session.delete(entity)
        await session.commit()
        return {"message": "Entity deleted"}
