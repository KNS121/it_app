import sys
from pathlib import Path
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from datetime import datetime

from sqlalchemy.dialects.postgresql import ENUM

PROJECT_ROOT = str(Path(__file__).parent.parent.parent.resolve())
sys.path.insert(0, PROJECT_ROOT)

from app.auth import get_password_hash

revision = '7728eb903f7a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Создаем ENUM тип для ролей
    user_roles = ENUM("student", "teacher", name="user_roles", create_type=True)
    user_roles.create(op.get_bind(), checkfirst=True)

    # 2. Создаем таблицу users
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("email", sa.String(100), unique=True, nullable=False),
        sa.Column("first_name", sa.String(50), nullable=False),
        sa.Column("last_name", sa.String(50), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("role", user_roles, nullable=False),  # Используем ENUM тип
        sa.Column("is_active", sa.Boolean, default=True),
    )

    # Создаем остальные таблицы
    op.create_table(
        'groups',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('number', sa.String(20), unique=True, nullable=False),
    )

    op.create_table(
        'subjects',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('type', sa.String(20), nullable=False),
        sa.Column('teacher_id', sa.Integer, nullable=False),
    )

    # Добавляем данные
    users_table = sa.table(
        'users',
        sa.Column('email', sa.String(100)),
        sa.Column('first_name', sa.String(50)),
        sa.Column('last_name', sa.String(50)),
        sa.Column('hashed_password', sa.String(255)),
        sa.Column('role', user_roles),
        sa.Column('is_active', sa.Boolean)
    )

    op.bulk_insert(
        sa.table(
            "users",
            sa.Column("email"),
            sa.Column("first_name"),
            sa.Column("last_name"),
            sa.Column("hashed_password"),
            sa.Column("role"),
            sa.Column("is_active"),
        ),
        [
            {
                "email": "teacher@edu.ru",
                "first_name": "Препод",
                "last_name": "Преподов",
                "hashed_password": get_password_hash("teacher123"),
                "role": "teacher",  # Просто строка, ENUM конвертируется автоматически
                "is_active": True,
            },
            {
                "email": "student@edu.ru",
                "first_name": "Студент",
                "last_name": "Студентов",
                "hashed_password": get_password_hash("student456"),
                "role": "student",  # Аналогично
                "is_active": True,
            },
        ],
    )

    op.bulk_insert(
        sa.table('groups', sa.Column('number')),
        [{'number': 'ГРУЗ-200'}]
    )

    op.bulk_insert(
        sa.table('teachers', sa.Column('user_id'), sa.Column('position')),
        [{'user_id': 1, 'position': 'Профессор'}]
    )

    op.bulk_insert(
        sa.table('students', sa.Column('user_id'), sa.Column('group_id')),
        [{'user_id': 2, 'group_id': 1}]
    )

    op.bulk_insert(
        sa.table('subjects', sa.Column('name'), sa.Column('type'), sa.Column('teacher_id')),
        [{
            "name": "ГОЙДАнных",
            "type": "practice",
            "teacher_id": 1
        }]
    )

    op.bulk_insert(
        sa.table('group_subject', sa.Column('group_id'), sa.Column('subject_id')),
        [{'group_id': 1, 'subject_id': 1}]
    )

    op.bulk_insert(
        sa.table(
            'course_materials',
            sa.Column('title'),
            sa.Column('file_path'),
            sa.Column('type'),
            sa.Column('deadline'),
            sa.Column('subject_id'),
            sa.Column('group_id')
        ),
        [{
            "title": "Введение хуя за щеку",
            "file_path": "/materials/sql_intro.pdf",
            "type": "lecture",
            "deadline": datetime(2025, 12, 12, 12, 00),
            "subject_id": 1,
            "group_id": 1
        }]
    )


def downgrade():
    # Удаляем данные в правильном порядке
    op.execute("DELETE FROM course_materials")
    op.execute("DELETE FROM group_subject")
    op.execute("DELETE FROM subjects")
    op.execute("DELETE FROM students")
    op.execute("DELETE FROM teachers")
    op.execute("DELETE FROM groups")
    op.execute("DELETE FROM users")

    # Удаляем ENUM тип
    op.execute("DROP TYPE IF EXISTS user_roles")

    # Удаляем таблицы
    op.drop_table('course_materials')
    op.drop_table('group_subject')
    op.drop_table('subjects')
    op.drop_table('students')
    op.drop_table('teachers')
    op.drop_table('groups')
    op.drop_table('users')