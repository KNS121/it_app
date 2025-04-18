import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import schemas
from app.models import models
from app.database import get_db

router = APIRouter(prefix="/groups", tags=["groups"])

@router.get("/{group_id}", response_model=schemas.GroupResponse)
async def get_group(group_id: int, db: AsyncSession = Depends(get_db)):
    group = await db.get(models.Group, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    return group