from pydantic import BaseModel, EmailStr, ConfigDict, Field
from datetime import datetime
from typing import Optional, Literal

# ========== Auth Schemas ==========
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str | None = None

# ========== User Schemas ==========
class UserBase(BaseModel):
    email: EmailStr
    first_name: str = Field(..., max_length=50)
    last_name: str = Field(..., max_length=50)
    patronymic: Optional[str] = Field(None, max_length=50)

# class UserCreate(UserBase):
#     password: str
#     role: Literal['student', 'teacher']

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    first_name: str
    last_name: str
    role: str
    is_active: bool

    class Config:
        from_attributes = True


# ========== Subject Schemas ==========
class SubjectBase(BaseModel):
    name: str = Field(..., max_length=100)
    type: Literal['lecture', 'practice']

class SubjectCreate(SubjectBase):
    teacher_id: int

class SubjectResponse(SubjectBase):
    id: int
    teacher_id: int
    groups: list[int]  # Group IDs

    model_config = ConfigDict(from_attributes=True)

# ========== Course Material Schemas ==========
class MaterialBase(BaseModel):
    title: str = Field(..., max_length=100)
    description: Optional[str] = None
    type: Literal['lecture', 'practice', 'assignment']
    deadline: Optional[datetime] = None

class MaterialCreate(MaterialBase):
    group_id: int

class MaterialResponse(MaterialBase):
    id: int
    subject_id: int
    group_id: int
    file_path: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# ========== Assignment Submission Schemas ==========
class SubmissionBase(BaseModel):
    feedback: Optional[str] = None
    grade: Optional[int] = Field(None, ge=0, le=100)
    status: Optional[Literal['submitted', 'graded', 'rejected']] = 'submitted'

class SubmissionCreate(BaseModel):
    file_path: str  # Path to uploaded file

class SubmissionResponse(SubmissionBase):
    id: int
    submission_date: datetime
    student_id: int
    material_id: int
    file_path: str

    model_config = ConfigDict(from_attributes=True)

class SubmissionGrade(BaseModel):  #
    grade: int = Field(..., ge=0, le=100)
    feedback: Optional[str] = None
    status: Literal['graded', 'rejected']

# ========== Group Schemas ==========
class GroupResponse(BaseModel):
    id: int
    number: str
    students: list[int]  # Student user_ids

    model_config = ConfigDict(from_attributes=True)

# ========== Schedule Schemas ==========
class ScheduleBase(BaseModel):
    start_time: datetime
    end_time: datetime
    subject_id: int

class ScheduleResponse(ScheduleBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

class UserCreate(BaseModel):
    email: EmailStr
    first_name: str = Field(..., max_length=50)
    last_name: str = Field(..., max_length=50)
    patronymic: Optional[str] = Field(None, max_length=50)
    password: str
    role: Literal['student', 'teacher']


class SubjectStudentView(BaseModel):
    subject: dict
    materials: list[dict]
    group_info: dict

    model_config = ConfigDict(from_attributes=True)

class CourseMaterialResponse(BaseModel):
    id: int
    title: str
    type: Literal['lecture', 'practice', 'assignment']
    description: Optional[str]
    deadline: Optional[datetime]
    created_at: datetime
    file_path: str

class AssignmentStatusResponse(BaseModel):
    material_id: int
    title: str
    deadline: Optional[datetime]
    status: Literal['not_started', 'submitted', 'graded', 'rejected']
    grade: Optional[int] = Field(None, ge=0, le=100)


class DeadlineResponse(BaseModel):
    id: int
    title: str
    deadline: datetime
    subject_id: int
    group_id: int
    file_path: Optional[str] = None  # Если нужно отображать прикрепленный файл

    model_config = ConfigDict(from_attributes=True)