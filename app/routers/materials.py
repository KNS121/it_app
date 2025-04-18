import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import schemas
from app.models import models
from app import database
from app.auth import get_current_user
import shutil


router = APIRouter(prefix="/materials", tags=["materials"])


@router.post("/", response_model=schemas.MaterialResponse)
async def upload_material(
        material: schemas.MaterialCreate,
        file: UploadFile = File(...),
        db: AsyncSession = Depends(database.get_db),
        current_user: models.User = Depends(get_current_user)
):
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can upload materials")

    # Сохранение файла
    file_path = Path(f"uploads/{file.filename}")
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    db_material = models.CourseMaterial(
        **material.dict(),
        file_path=str(file_path),
        teacher_id=current_user.id
    )

    db.add(db_material)
    await db.commit()
    return db_material


@router.get("/{subject_id}", response_model=list[schemas.MaterialResponse])
async def get_subject_materials(
        subject_id: int,
        db: AsyncSession = Depends(database.get_db),
        current_user: models.User = Depends(get_current_user)
):
    # Проверка прав доступа
    subject = await db.get(models.Subject, subject_id)
    if current_user.role == "student" and not any(
            g.id == current_user.student_profile.group_id for g in subject.groups
    ):
        raise HTTPException(status_code=403, detail="Access denied")

    return subject.materials