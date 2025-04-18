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

router = APIRouter(prefix="/calendar", tags=["calendar"])


@router.get("/deadlines", response_model=list[schemas.DeadlineResponse])
async def get_deadlines(
        db: AsyncSession = Depends(database.get_db),
        current_user: models.User = Depends(get_current_user)
):
    query = select(models.CourseMaterial).where(
        models.CourseMaterial.deadline.isnot(None)
    )

    if current_user.role == "student":
        query = query.join(models.Group).where(
            models.Group.id == current_user.student_profile.group_id
        )
    elif current_user.role == "teacher":
        query = query.where(
            models.CourseMaterial.teacher_id == current_user.id
        )

    result = await db.execute(query)
    return result.scalars().all()


@router.get("/schedule", response_model=list[schemas.ScheduleResponse])
async def get_schedule(
        db: AsyncSession = Depends(database.get_db),
        current_user: models.User = Depends(get_current_user)
):
    if current_user.role == "student":
        group_id = current_user.student_profile.group_id
        return await db.execute(
            select(models.Schedule)
            .join(models.Subject)
            .join(models.Group)
            .where(models.Group.id == group_id)
        ).scalars().all()
    else:
        return await db.execute(
            select(models.Schedule)
            .join(models.Subject)
            .where(models.Subject.teacher_id == current_user.id)
        ).scalars().all()