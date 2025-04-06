from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.future import select
from fastapi import HTTPException

from app.dao.base import BaseDAO
from app.users.models import User, Role, UserRoles


class UsersDAO(BaseDAO):
    model = User

    @classmethod
    async def create_role(cls, session: AsyncSession, role_name: str):
        existing_role = await session.execute(select(Role).filter_by(name=role_name))
        if existing_role.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Role already exists")

        new_role = Role(name=role_name)
        session.add(new_role)
        await session.commit()
        return new_role

    @classmethod
    async def assign_role_to_user(cls, session: AsyncSession, user_id: int, role_name: str):
        user = await session.execute(select(User).options(selectinload(User.roles)).filter_by(id=user_id))
        user = user.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        role = await session.execute(select(Role).filter_by(name=role_name))
        role = role.scalar_one_or_none()
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")

        user_role = UserRoles(user_id=user.id, role_id=role.id)
        session.add(user_role)
        await session.commit()
        return {"message": f"Role '{role_name}' assigned to user {user_id}"}
