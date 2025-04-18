import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import schemas
from app.models import models
from app import database
from app.auth import get_current_user
from sqlalchemy import select

router = APIRouter(prefix="/subjects", tags=["subjects"])


@router.post("/", response_model=schemas.SubjectResponse)
async def create_subject(
        subject: schemas.SubjectCreate,
        db: AsyncSession = Depends(database.get_db),
        current_user: models.User = Depends(get_current_user)
):
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can create subjects")

    db_subject = models.Subject(**subject.dict(), teacher_id=current_user.id)
    db.add(db_subject)
    await db.commit()
    return db_subject


@router.get("/my", response_model=list[schemas.SubjectResponse])
async def get_my_subjects(
        db: AsyncSession = Depends(database.get_db),
        current_user: models.User = Depends(get_current_user)
):
    if current_user.role == "teacher":
        return current_user.teacher_profile.subjects
    else:
        student = await db.execute(
            select(models.Student).where(models.Student.user_id == current_user.id)
        )
        student = student.scalar()
        return student.group.subjects