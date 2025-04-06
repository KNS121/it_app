from sqlalchemy import String, ForeignKey, Computed
from geoalchemy2 import Geometry
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base, int_pk
import json

class Field(Base):
    __tablename__ = "fields"

    id: Mapped[int_pk]
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    field_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    geometry = mapped_column(Geometry('POLYGON', srid=4326), nullable=False)
    soil_type: Mapped[str] = mapped_column(String(100), nullable=False)
    area_hectares: Mapped[float] = mapped_column(Computed("ST_Area(geometry::geography) / 10000"))
    crop_rotation: Mapped[str] = mapped_column(String(200), nullable=True)
    cultivation_technology: Mapped[str] = mapped_column(String(200), nullable=True)
    farmer_id: Mapped[int] = mapped_column(ForeignKey("farmers.id"), nullable=False)

    farmer: Mapped["Farmer"] = relationship("Farmer", back_populates="fields")

    def to_geojson(self):
        return {
            "type": "Feature",
            "geometry": json.loads(self.geometry.ST_AsGeoJSON()),
            "properties": {
                "id": self.id,
                "name": self.name,
                "field_number": self.field_number,
                "soil_type": self.soil_type,
                "area_hectares": self.area_hectares
            }
        }
