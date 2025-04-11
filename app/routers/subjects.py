from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.schemas.schemas import Subject, SubjectCreate
from app.models.models import Subject as DBSubject, User
from app.database import get_db
from app.auth import get_current_user

router = APIRouter(prefix="/subjects", tags=["subjects"])

@router.post("/", response_model=Subject)
async def create_subject(
    subject: SubjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_teacher:
        raise HTTPException(403, "Только для преподавателей")
    
    db_subject = DBSubject(**subject.dict(), teacher_id=current_user.id)
    db.add(db_subject)
    await db.commit()
    return db_subject

@router.get("/", response_model=list[Subject])
async def get_subjects(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DBSubject))
    return result.scalars().all()

@router.post("/{subject_id}/enroll/{student_id}")
async def enroll_student(
    subject_id: int,
    student_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Проверка что текущий пользователь - преподаватель предмета
    subject = await db.get(DBSubject, subject_id)
    if not subject or subject.teacher_id != current_user.id:
        raise HTTPException(404, "Предмет не найден или доступ запрещен")
    
    student = await db.get(User, student_id)
    if not student or student.is_teacher:
        raise HTTPException(404, "Студент не найден")
    
    subject.students.append(student)
    await db.commit()
    return {"message": "Студент успешно записан"}