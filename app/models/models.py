from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum, Text, Table, Boolean, CheckConstraint
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

#Base = declarative_base()
from app.database import Base

# Ассоциативная таблица для связи групп и предметов
group_subject = Table(
    'group_subject',
    Base.metadata,
    Column('group_id', ForeignKey('groups.id'), primary_key=True),
    Column('subject_id', ForeignKey('subjects.id'), primary_key=True)
)


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    patronymic = Column(String(50))
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum('student', 'teacher', name='user_roles'), nullable=False)
    is_active = Column(Boolean, default=True)

    # Relationships
    student_profile = relationship("Student", back_populates="user", uselist=False, cascade="all, delete-orphan")
    teacher_profile = relationship("Teacher", back_populates="user", uselist=False, cascade="all, delete-orphan")


class Student(Base):
    __tablename__ = 'students'

    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    group_id = Column(Integer, ForeignKey('groups.id'))

    user = relationship("User", back_populates="student_profile")
    group = relationship("Group", back_populates="students")
    submissions = relationship("AssignmentSubmission", back_populates="student")


class Teacher(Base):
    __tablename__ = 'teachers'

    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    position = Column(String(100), nullable=False)

    user = relationship("User", back_populates="teacher_profile")
    subjects = relationship("Subject", back_populates="teacher", cascade="all, delete-orphan")


class Group(Base):
    __tablename__ = 'groups'

    id = Column(Integer, primary_key=True)
    number = Column(String(20), unique=True, nullable=False)

    students = relationship("Student", back_populates="group")
    subjects = relationship("Subject", secondary=group_subject, back_populates="groups")


class Subject(Base):
    __tablename__ = 'subjects'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    type = Column(Enum('lecture', 'practice', name='subject_types'), nullable=False)
    teacher_id = Column(Integer, ForeignKey('teachers.user_id'), nullable=False)

    teacher = relationship("Teacher", back_populates="subjects")
    groups = relationship("Group", secondary=group_subject, back_populates="subjects")
    materials = relationship("CourseMaterial", back_populates="subject")
    schedule = relationship("Schedule", back_populates="subject")


class CourseMaterial(Base):
    __tablename__ = 'course_materials'

    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    file_path = Column(String(255), nullable=False)
    description = Column(Text)
    type = Column(Enum('lecture', 'practice', 'assignment', name='material_types'), nullable=False)
    deadline = Column(DateTime)
    subject_id = Column(Integer, ForeignKey('subjects.id'), nullable=False)
    group_id = Column(Integer, ForeignKey('groups.id'), nullable=False)

    subject = relationship("Subject", back_populates="materials")
    group = relationship("Group")
    submissions = relationship("AssignmentSubmission", back_populates="material")

    __table_args__ = (
        CheckConstraint('deadline > CURRENT_TIMESTAMP', name='check_future_deadline'),
    )


class AssignmentSubmission(Base):
    __tablename__ = 'assignment_submissions'

    id = Column(Integer, primary_key=True)
    submission_date = Column(DateTime, default=datetime.utcnow)
    status = Column(Enum('submitted', 'graded', 'rejected', name='submission_status'), default='submitted')
    grade = Column(Integer)
    feedback = Column(Text)
    file_path = Column(String(255))
    student_id = Column(Integer, ForeignKey('students.user_id'), nullable=False)
    material_id = Column(Integer, ForeignKey('course_materials.id'), nullable=False)

    student = relationship("Student", back_populates="submissions")
    material = relationship("CourseMaterial", back_populates="submissions")

    __table_args__ = (
        CheckConstraint('grade BETWEEN 0 AND 100', name='grade_range_check'),
    )


class Schedule(Base):
    __tablename__ = 'schedules'

    id = Column(Integer, primary_key=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    #event_type = Column(Enum('lesson', 'office_hours', 'meeting', name='schedule_types'), default='lesson')
    subject_id = Column(Integer, ForeignKey('subjects.id'), nullable=False)

    subject = relationship("Subject", back_populates="schedule")

    __table_args__ = (
        CheckConstraint('end_time > start_time', name='check_time_order'),
    )
