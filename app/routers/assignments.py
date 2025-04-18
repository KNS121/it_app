import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))  # Добавляем корень проекта в PYTHONPATH

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import schemas
from app.models import models
from app import database
from app.auth import get_current_user
from datetime import datetime

router = APIRouter(prefix="/assignments", tags=["assignments"])


@router.post("/submit", response_model=schemas.SubmissionResponse)
async def submit_assignment(
        submission: schemas.SubmissionCreate,
        db: AsyncSession = Depends(database.get_db),
        current_user: models.User = Depends(get_current_user)
):
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Only students can submit assignments")

    material = await db.get(models.CourseMaterial, submission.material_id)
    if material.deadline and material.deadline < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Deadline has passed")

    db_submission = models.AssignmentSubmission(
        **submission.dict(),
        student_id=current_user.id
    )

    db.add(db_submission)
    await db.commit()
    return db_submission


@router.patch("/{submission_id}", response_model=schemas.SubmissionResponse)
async def grade_assignment(
        submission_id: int,
        grade_data: schemas.SubmissionGrade,
        db: AsyncSession = Depends(database.get_db),
        current_user: models.User = Depends(get_current_user)
):
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can grade assignments")

    submission = await db.get(models.AssignmentSubmission, submission_id)
    submission.grade = grade_data.grade
    submission.status = "graded"
    await db.commit()
    return submission