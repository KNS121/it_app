import folium


# Функция для создания карты с маркером
def create_map(lat, lon):
    # Создаем карту с центром в указанных координатах
    map_object = folium.Map(location=[lat, lon], zoom_start=15)

    # Добавляем маркер
    folium.Marker([lat, lon], popup="Расположение объекта").add_to(map_object)

    # Сохраняем карту в HTML файл
    map_object.save('map.html')
