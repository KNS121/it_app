from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

# Ассоциативная таблица для связи студентов и предметов
student_subject = Table(
    'student_subject',
    Base.metadata,
    Column('student_id', ForeignKey('users.id'), primary_key=True),
    Column('subject_id', ForeignKey('subjects.id'), primary_key=True)
)

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255))
    full_name = Column(String(100))
    is_teacher = Column(Boolean, default=False)
    
    # Для преподавателя
    taught_subjects = relationship("Subject", back_populates="teacher")
    
    # Для студента
    enrolled_subjects = relationship("Subject", secondary=student_subject, back_populates="students")

class Subject(Base):
    __tablename__ = "subjects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True)
    description = Column(Text)
    teacher_id = Column(Integer, ForeignKey("users.id"))
    
    teacher = relationship("User", back_populates="taught_subjects")
    students = relationship("User", secondary=student_subject, back_populates="enrolled_subjects")
    materials = relationship("Material", back_populates="subject")
    assignments = relationship("Assignment", back_populates="subject")

class Material(Base):
    __tablename__ = "materials"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100))
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    
    subject = relationship("Subject", back_populates="materials")

class Assignment(Base):
    __tablename__ = "assignments"
    
    id = Column(Integer, primary_key=True)
    title = Column(String(100))
    description = Column(Text)
    deadline = Column(DateTime)
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    
    subject = relationship("Subject", back_populates="assignments")
    submissions = relationship("Submission", back_populates="assignment")

class Submission(Base):
    __tablename__ = "submissions"
    
    id = Column(Integer, primary_key=True)
    content = Column(Text)
    submitted_at = Column(DateTime, default=datetime.utcnow)
    student_id = Column(Integer, ForeignKey("users.id"))
    assignment_id = Column(Integer, ForeignKey("assignments.id"))
    
    assignment = relationship("Assignment", back_populates="submissions")
    student = relationship("User")