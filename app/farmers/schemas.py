from datetime import date
from typing import Optional, List
import re
from pydantic import BaseModel, Field, EmailStr, ConfigDict, field_validator

from app.fields.schemas import SField


class SFarmerBase(BaseModel):
    phone_number: str = Field(..., max_length=15, description="Номер телефона в международном формате, начинающийся с '+'")
    first_name: str = Field(..., min_length=1, max_length=50, description="Имя фермера, от 1 до 50 символов")
    last_name: str = Field(..., min_length=1, max_length=50, description="Фамилия фермера, от 1 до 50 символов")
    date_of_birth: date = Field(..., description="Дата рождения фермера в формате ГГГГ-ММ-ДД")
    email: EmailStr = Field(..., description="Электронная почта фермера")
    address: str = Field(..., min_length=10, max_length=200, description="Адрес фермера, не более 200 символов")
    photo: Optional[str] = Field(None, max_length=100, description="Фото фермера")

    @field_validator("phone_number", mode="before")
    @classmethod
    def validate_phone_number(cls, value):
        if not re.match(r'^\+\d{1,15}$', value):
            raise ValueError('Номер телефона должен начинаться с "+" и содержать от 1 до 15 цифр')
        return value

    @field_validator("date_of_birth", mode="before")
    @classmethod
    def validate_date_of_birth(cls, value):
        if value >= date.today():
            raise ValueError('Дата рождения должна быть в прошлом')
        return value


class SFarmer(SFarmerBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    fields: List[SField] = Field(default_factory=list, description="Список полей")

    @property
    def number_of_fields(self) -> int:
        """Возвращает количество полей у фермера."""
        return len(self.fields)

    @property
    def total_area_hectares(self) -> float:
        """Возвращает общую площадь всех полей в гектарах."""
        return sum(field.area_hectares for field in self.fields)


class SFarmerAdd(SFarmerBase):
    class Config:
        json_schema_extra = {
            "example": {
                "phone_number": "+79261234567",
                "first_name": "Иван",
                "last_name": "Иванов",
                "date_of_birth": "1980-05-10",
                "email": "ivan.ivanov@example.com",
                "address": "Тульская область, Россия",
                "photo": "https://example.com/photo.jpg"
            }
        }


class SFarmerUpdDesc(SFarmerBase):
    phone_number: Optional[str] = Field(None, max_length=15, description="Номер телефона в международном формате, начинающийся с '+'")
    first_name: Optional[str] = Field(None, min_length=1, max_length=50, description="Имя фермера, от 1 до 50 символов")
    last_name: Optional[str] = Field(None, min_length=1, max_length=50, description="Фамилия фермера, от 1 до 50 символов")
    date_of_birth: Optional[date] = Field(None, description="Дата рождения фермера в формате ГГГГ-ММ-ДД")
    email: Optional[EmailStr] = Field(None, description="Электронная почта фермера")
    address: Optional[str] = Field(None, min_length=10, max_length=200, description="Адрес фермера, не более 200 символов")
    photo: Optional[str] = Field(None, max_length=100, description="Фото фермера")

