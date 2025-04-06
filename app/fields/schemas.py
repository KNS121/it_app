from pydantic import BaseModel, Field, ConfigDict, model_validator
from typing import List, Optional

class CoordinatePoint(BaseModel):
    lat: float = Field(
        ...,
        ge=-90,
        le=90,
        example=55.755825,
        description="Широта в градусах (WGS84)"
    )
    lon: float = Field(
        ...,
        ge=-180,
        le=180,
        example=37.617298,
        description="Долгота в градусах (WGS84)"
    )

class SFieldBase(BaseModel):
    name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        example="Главное поле",
        description="Уникальное название поля"
    )
    field_number: str = Field(
        ...,
        example="F-2023-001",
        description="Уникальный номер поля"
    )
    soil_type: str = Field(
        ...,
        example="Чернозем",
        description="Тип почвы"
    )
    coordinates: List[CoordinatePoint] = Field(
        ...,
        min_length=3,
        description="Список координат полигона (минимум 3 точки)"
    )
    crop_rotation: Optional[str] = Field(
        None,
        max_length=200,
        example="Пшеница-Кукуруза-Гречиха",
        description="Схема севооборота"
    )
    cultivation_technology: Optional[str] = Field(
        None,
        max_length=200,
        example="No-Till",
        description="Технология возделывания"
    )

    @model_validator(mode='after')
    def validate_and_convert(self):
        coords = self.coordinates

        if len(coords) < 3:
            raise ValueError("Требуется минимум 3 точки для полигона")

        # Замыкаем полигон если необходимо
        if coords[0] != coords[-1]:
            coords.append(coords[0])

        # Преобразуем в WKT с правильным порядком координат
        points = [f"{p.lon} {p.lat}" for p in coords]
        wkt_coords = ", ".join(points)
        self.model_config.extra = {"geometry": f"SRID=4326;POLYGON(({wkt_coords}))"}
        return self


class SFieldCreate(SFieldBase):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Восточное поле",
                "field_number": "F-2023-001",
                "soil_type": "Чернозем",
                "coordinates": [
                    {"lat": 55.755825, "lon": 37.617298},
                    {"lat": 55.751952, "lon": 37.626534},
                    {"lat": 55.746144, "lon": 37.623478}
                ],
                "crop_rotation": "Пшеница-Рожь-Овес",
                "cultivation_technology": "No-Till"
            }
        }
    )


class SFieldUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    field_number: Optional[str] = Field(None, description="Уникальный номер поля")
    soil_type: Optional[str] = Field(None, description="Тип почвы")
    coordinates: Optional[List[CoordinatePoint]] = Field(None, min_length=3)
    crop_rotation: Optional[str] = Field(None, max_length=200)
    cultivation_technology: Optional[str] = Field(None, max_length=200)


class SFieldFilter(BaseModel):
    name: Optional[str] = None
    field_number: Optional[str] = None
    soil_type: Optional[str] = None
    farmer_id: Optional[int] = None
    min_area: Optional[float] = Field(None, ge=0)
    max_area: Optional[float] = Field(None, ge=0)
    crop_rotation: Optional[str] = None


class SField(SFieldBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    farmer_id: int
    area_hectares: float


class SFieldResponse(SField):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "Восточное поле",
                "field_number": "F-2023-001",
                "soil_type": "Чернозем",
                "area_hectares": 12.45,
                "farmer_id": 5,
                "coordinates": [
                    {"lat": 55.755825, "lon": 37.617298},
                    {"lat": 55.751952, "lon": 37.626534},
                    {"lat": 55.746144, "lon": 37.623478},
                    {"lat": 55.755825, "lon": 37.617298}
                ],
                "crop_rotation": "Пшеница-Рожь-Овес",
                "cultivation_technology": "No-Till"
            }
        }
    )
