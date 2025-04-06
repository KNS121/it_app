class RBFarmer:
    def __init__(self, farmer_id: int | None = None,
                 first_name: str | None = None,
                 last_name: str | None = None):
        self.id = farmer_id
        self.first_name = first_name
        self.last_name = last_name

    def to_dict(self) -> dict:
        data = {'id': self.id, 'first_name': self.first_name, 'last_name': self.last_name}
        # Создаем копию словаря, чтобы избежать изменения словаря во время итерации
        filtered_data = {key: value for key, value in data.items() if value is not None}
        return filtered_data
