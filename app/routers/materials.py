from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.schemas.schemas import Material, MaterialCreate
from app.models.models import Material as DBMaterial, Subject, User
from app.database import get_db
from app.auth import get_current_user

router = APIRouter(prefix="/materials", tags=["materials"])

@router.post("/", response_model=Material)
async def create_material(
    material: MaterialCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Проверка что пользователь - преподаватель предмета
    subject = await db.get(Subject, material.subject_id)
    if not subject or subject.teacher_id != current_user.id:
        raise HTTPException(403, "Нет прав на создание материала")
    
    db_material = DBMaterial(**material.dict())
    db.add(db_material)
    await db.commit()
    return db_material

@router.get("/subject/{subject_id}", response_model=list[Material])
async def get_subject_materials(
    subject_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Проверка что студент записан на предмет или преподаватель
    subject = await db.get(Subject, subject_id)
    if not subject:
        raise HTTPException(404, "Предмет не найден")
    
    if current_user.is_teacher and subject.teacher_id != current_user.id:
        raise HTTPException(403, "Доступ запрещен")
    
    if not current_user.is_teacher and current_user not in subject.students:
        raise HTTPException(403, "Вы не записаны на этот предмет")
    
    result = await db.execute(select(DBMaterial).where(DBMaterial.subject_id == subject_id))
    return result.scalars().all()