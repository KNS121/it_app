from app.database import Base, str_uniq, int_pk, str_null_true
from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import date
import json

# from app.fields.models import Field


# Модель Фермера
class Farmer(Base):
    id: Mapped[int_pk]
    phone_number: Mapped[str_uniq]
    first_name: Mapped[str]
    last_name: Mapped[str]
    farm_name: Mapped[str]
    date_of_birth: Mapped[date]
    email: Mapped[str_uniq]

    address: Mapped[str] = mapped_column(Text, nullable=False)
    photo: Mapped[str] = mapped_column(Text, nullable=True)

    # Отношение с полями
    fields: Mapped[list["Field"]] = relationship("Field", back_populates="farmer", cascade="all, delete-orphan")

    @property
    def number_of_fields(self) -> int:
        """Возвращает количество полей у фермера."""
        return len(self.fields)

    @property
    def total_area_hectares(self) -> float:
        """Возвращает общую площадь всех полей в гектарах."""
        return sum(field.area_hectares for field in self.fields)

    def __str__(self):
        return (f"{self.__class__.__name__}(id={self.id}, "
                f"first_name={self.first_name!r}, "
                f"last_name={self.last_name!r})")

    def __repr__(self):
        return str(self)

    def to_dict(self):
        return {
            "id": self.id,
            "phone_number": self.phone_number,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "date_of_birth": self.date_of_birth,
            "email": self.email,
            "address": self.address,
            "photo": self.photo,
            "fields": [field.to_dict() for field in self.fields]
        }


# # Модель Поля
# class Field(Base):
#     id: Mapped[int_pk]
#     name: Mapped[str_uniq]
#     area_hectares: Mapped[float] = mapped_column(Float, nullable=False)
#     crop_rotation: Mapped[str] = mapped_column(String, nullable=True)
#     cultivation_technology: Mapped[str] = mapped_column(String, nullable=True)
#     coordinates: Mapped[str] = mapped_column(String, nullable=True)
#
#     # Внешний ключ, связывающий поле с фермером
#     farmer_id: Mapped[int] = mapped_column(ForeignKey("farmers.id"), nullable=True)
#
#     # Связь с моделью Farmer (отношение многие-к-одному)
#     farmer: Mapped["Farmer"] = relationship("Farmer", back_populates="fields")
#
#     @property
#     def parsed_coordinates(self):
#         """Возвращает координаты как список точек (словарей)"""
#         return json.loads(self.coordinates) if self.coordinates else []
#
#     def __str__(self):
#         return f"{self.__class__.__name__}(id={self.id}, name={self.name!r})"
#
#     def __repr__(self):
#         return str(self)
#
#     def to_dict(self):
#         return {
#             "id": self.id,
#             "name": self.name,
#             "area_hectares": self.area_hectares,
#             "crop_rotation": self.crop_rotation,
#             "cultivation_technology": self.cultivation_technology,
#             "coordinates": self.coordinates,
#             "farmer_id": self.farmer_id
#         }
