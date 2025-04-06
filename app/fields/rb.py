class RBField:
    def __init__(self, field_id: int | None = None,
                 name: str | None = None,
                 area_hectares: float | None = None,
                 crop_rotation: str | None = None,
                 cultivation_technology: str | None = None,
                 coordinates: str | None = None,
                 farmer_id: int | None = None):
        self.id = field_id
        self.name = name
        self.area_hectares = area_hectares
        self.crop_rotation = crop_rotation
        self.cultivation_technology = cultivation_technology
        self.coordinates = coordinates
        self.farmer_id = farmer_id

    def to_dict(self) -> dict:
        data = {
            'id': self.id,
            'name': self.name,
            'area_hectares': self.area_hectares,
            'crop_rotation': self.crop_rotation,
            'cultivation_technology': self.cultivation_technology,
            'coordinates': self.coordinates,
            'farmer_id': self.farmer_id
        }
        # Фильтрация полей со значением None
        filtered_data = {key: value for key, value in data.items() if value is not None}
        return filtered_data
