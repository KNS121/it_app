# from fastapi import FastAPI, Request
# from fastapi.responses import HTMLResponse
# import folium
#
# app = FastAPI()
#
#
# # Функция для создания карты с маркером
# def create_map(lat, lon):
#     # Создаем карту с центром в указанных координатах
#     map_object = folium.Map(location=[lat, lon], zoom_start=15)
#
#     # Добавляем маркер
#     folium.Marker([lat, lon], popup="Расположение объекта").add_to(map_object)
#
#     # Сохраняем карту в HTML файл
#     map_object.save('map.html')
#
#
# # Эндпоинт для отображения формы ввода координат
# @app.get("/", response_class=HTMLResponse)
# async def get_form():
#     return '''
#     <form method="post" action="/create_map">
#         <label>Широта: <input type="text" name="latitude"></label><br>
#         <label>Долгота: <input type="text" name="longitude"></label><br>
#         <button type="submit">Создать карту</button>
#     </form>
#     '''
#
#
# # Эндпоинт для обработки данных и создания карты
# @app.post("/create_map", response_class=HTMLResponse)
# async def create_map_form(request: Request):
#     form_data = await request.form()
#     lat = float(form_data['latitude'])
#     lon = float(form_data['longitude'])
#
#     # Создание карты с координатами
#     create_map(lat, lon)
#
#     # Чтение сгенерированного HTML файла и возвращение пользователю
#     with open('../map.html', 'r', encoding='utf-8') as f:
#         html_content = f.read()
#
#     return HTMLResponse(content=html_content)

from fastapi import FastAPI
from fastapi.responses import HTMLResponse


app = FastAPI()


@app.get("/", response_class=HTMLResponse)
async def root():
    # HTML-код для формы ввода координат
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Карта полей</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 20px;
                padding: 0;
                background-color: #f4f4f4;
            }
            h1 {
                text-align: center;
            }
            form {
                display: flex;
                flex-direction: column;
                align-items: center;
                margin-bottom: 20px;
            }
            input {
                margin: 5px;
                padding: 10px;
                width: 200px;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
            button {
                padding: 10px 15px;
                border: none;
                background-color: #28a745;
                color: white;
                border-radius: 4px;
                cursor: pointer;
            }
            button:hover {
                background-color: #218838;
            }
            #map {
                width: 100%;
                height: 500px;
            }
        </style>
        <script src="https://api-maps.yandex.ru/2.1/?lang=ru_RU" type="text/javascript"></script>
    </head>
    <body>
        <h1>Карта полей</h1>
        <form id="coordinateForm" onsubmit="return showMap();">
            <input type="text" id="lat1" placeholder="Широта 1" required>
            <input type="text" id="lon1" placeholder="Долгота 1" required>
            <input type="text" id="lat2" placeholder="Широта 2" required>
            <input type="text" id="lon2" placeholder="Долгота 2" required>
            <input type="text" id="lat3" placeholder="Широта 3" required>
            <input type="text" id="lon3" placeholder="Долгота 3" required>
            <input type="text" id="lat4" placeholder="Широта 4" required>
            <input type="text" id="lon4" placeholder="Долгота 4" required>
            <button type="submit">Показать поле</button>
        </form>
        <div id="map"></div>

        <script type="text/javascript">
            var myMap;
            var polygon;

            function showMap() {
                var coords = [
                    [parseFloat(document.getElementById('lat1').value), parseFloat(document.getElementById('lon1').value)],
                    [parseFloat(document.getElementById('lat2').value), parseFloat(document.getElementById('lon2').value)],
                    [parseFloat(document.getElementById('lat3').value), parseFloat(document.getElementById('lon3').value)],
                    [parseFloat(document.getElementById('lat4').value), parseFloat(document.getElementById('lon4').value)]
                ];

                if (!myMap) {
                    myMap = new ymaps.Map('map', {
                        center: coords[0],
                        zoom: 12,
                        controls: ['zoomControl', 'typeSelector']
                    });
                    myMap.setType('yandex#hybrid');
                } else {
                    myMap.setCenter(coords[0]);
                    myMap.setZoom(12);
                    myMap.geoObjects.removeAll(); // Удаляем старые объекты
                }

                // Создаем и добавляем новый полигон
                polygon = new ymaps.Polygon([coords], {
                    balloonContent: 'Поле номер 1'
                }, {
                    fillColor: '#00FF0088',
                    strokeColor: '#0000FF',
                    strokeWidth: 2
                });

                myMap.geoObjects.add(polygon);
                return false; // Предотвращаем перезагрузку страницы
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)




