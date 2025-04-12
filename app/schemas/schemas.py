from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from typing import Optional

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: str

class UserCreate(UserBase):
    password: str
    is_teacher: bool

class UserResponse(UserBase):
    id: int
    is_teacher: bool

    model_config = ConfigDict(from_attributes=True)

# Auth Schemas
class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenData(BaseModel):
    email: str | None = None

# Subject Schemas
class SubjectBase(BaseModel):
    name: str
    description: str | None = None

class SubjectCreate(SubjectBase):
    pass

class Subject(SubjectBase):
    id: int
    teacher_id: int
    
    model_config = ConfigDict(from_attributes=True)

# Material Schemas
class MaterialBase(BaseModel):
    title: str
    content: str

class MaterialCreate(MaterialBase):
    pass

class Material(MaterialBase):
    id: int
    created_at: datetime
    subject_id: int
    
    model_config = ConfigDict(from_attributes=True)

# Assignment Schemas
class AssignmentBase(BaseModel):
    title: str
    description: str
    deadline: datetime

class AssignmentCreate(AssignmentBase):
    pass

class Assignment(AssignmentBase):
    id: int
    subject_id: int
    
    model_config = ConfigDict(from_attributes=True)

# Submission Schemas
class SubmissionBase(BaseModel):
    content: str

class SubmissionCreate(SubmissionBase):
    pass

class Submission(SubmissionBase):
    id: int
    submitted_at: datetime
    student_id: int
    assignment_id: int
    
    model_config = ConfigDict(from_attributes=True)

# Добавляем в конец файла
class User(UserResponse):
    """Алиас для совместимости"""
    pass