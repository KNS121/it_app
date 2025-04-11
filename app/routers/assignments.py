from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from app.schemas.schemas import Assignment, AssignmentCreate
from app.models.models import Assignment as DBAssignment, Subject, User
from app.database import get_db
from app.auth import get_current_user

router = APIRouter(prefix="/assignments", tags=["assignments"])

@router.post("/", response_model=Assignment)
async def create_assignment(
    assignment: AssignmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Проверка прав преподавателя
    subject = await db.get(Subject, assignment.subject_id)
    if not subject or subject.teacher_id != current_user.id:
        raise HTTPException(403, "Нет прав на создание задания")
    
    db_assignment = DBAssignment(**assignment.dict())
    db.add(db_assignment)
    await db.commit()
    return db_assignment

@router.get("/deadlines", response_model=list[dict])
async def get_deadlines(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = select(DBAssignment.title, DBAssignment.deadline)
    
    if current_user.is_teacher:
        result = await db.execute(query)
    else:
        result = await db.execute(
            query.join(Subject).where(Subject.students.any(id=current_user.id))
        )
    
    return [{"title": a.title, "deadline": a.deadline} for a in result.all()]