import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

import os
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
from sqlalchemy.dialects.postgresql import insert
from app.models import models
from app.auth import get_password_hash
import asyncio

DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost/edu_platform_db"
engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)

    async with async_session() as session:
        # Проверяем существование данных
        result = await session.execute(select(models.User).filter_by(email="teacher@edu.ru"))
        if not result.scalars().first():
            group = models.Group(number="ГРУЗ-200")
            session.add(group)
            await session.commit()

            teacher_user = models.User(
                first_name="Препод",
                last_name="Преподов",
                email="teacher@edu.ru",
                hashed_password=get_password_hash("teacher123"),
                role="teacher",
                is_active=True
            )

            student_user = models.User(
                first_name="Студент",
                last_name="Студентов",
                email="student@edu.ru",
                hashed_password=get_password_hash("student456"),
                role="student",
                is_active=True
            )

            session.add_all([teacher_user, student_user])
            await session.commit()

            teacher = models.Teacher(user_id=teacher_user.id, position="Профессор")
            student = models.Student(user_id=student_user.id, group_id=group.id)
            session.add_all([teacher, student])

            subject = models.Subject(
                name="Работа с данными",
                type="practice",
                teacher_id=teacher.user_id
            )
            session.add(subject)
            await session.commit()

            # Вставка данных в ассоциативную таблицу group_subject
            stmt = insert(models.group_subject).values(group_id=group.id, subject_id=subject.id)
            await session.execute(stmt)
            await session.commit()

            course_material = models.CourseMaterial(
                title="Введение в SQL",
                file_path="/materials/sql_intro.pdf",
                type="lecture",
                deadline=datetime(2025, 12, 12, 12, 0),
                subject_id=subject.id,
                group_id=group.id
            )
            session.add(course_material)
            await session.commit()

if __name__ == "__main__":
    asyncio.run(init_db())
