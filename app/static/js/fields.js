let map, drawnItems;
let coordinates = [];
let baseLayers = {};

function initMap() {
    const mapContainer = document.getElementById('map-container');
    if (!mapContainer || !document.getElementById('fields-map')) return;

    mapContainer.style.display = 'block';

    map = L.map('fields-map', {
        center: [55.751574, 37.573856],
        zoom: 10
    });

    // Создаем слои
    const esriSatellite = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
        attribution: 'Tiles © Esri'
    });

    const osmMap = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap'
    });

    const labels = L.tileLayer('https://{s}.basemaps.cartocdn.com/light_only_labels/{z}/{x}/{y}.png', {
        attribution: '© CARTO'
    });

    // Группируем слои
    baseLayers = {
        "Спутник": esriSatellite,
        "Схема": osmMap
    };

    // Добавляем управление слоями
    L.control.layers(baseLayers, {
        "Подписи": labels
    }, {
        collapsed: false,
        position: 'topright'
    }).addTo(map);

    // Первоначальная загрузка
    esriSatellite.addTo(map);
    labels.addTo(map);

    // Инициализация слоя рисования
    drawnItems = new L.FeatureGroup().addTo(map);

    // Инструменты рисования
    const drawControl = new L.Control.Draw({
        draw: {
            polygon: {
                shapeOptions: {
                    color: '#3388ff',
                    fillOpacity: 0.4
                },
                allowIntersection: false
            },
            circle: false,
            marker: false,
            polyline: false,
            rectangle: false
        },
        edit: {
            featureGroup: drawnItems
        }
    }).addTo(map);

    // Обработчики событий
    map.on(L.Draw.Event.CREATED, function(e) {
        const layer = e.layer;
        drawnItems.addLayer(layer);
        updateFromLayer(layer);
    });

    map.on('moveend', function() {
        map.invalidateSize();
    });

    // Обработчик изменения режима
    document.getElementById('coordinate-method').addEventListener('change', function(e) {
        toggleInputMode(e.target.value);
    });
}

function updateFromLayer(layer) {
    const geoJSON = layer.toGeoJSON();
    coordinates = geoJSON.geometry.coordinates[0].map(coord => [coord[1], coord[0]]);
    const area = turf.area(geoJSON);
    updateArea(area / 10000);
}

function updateArea(hectares) {
    document.getElementById('area').value = hectares.toFixed(2);
}

function toggleInputMode(mode) {
    const mapContainer = document.getElementById('map-container');
    const manualContainer = document.getElementById('manual-coordinates-container');

    if (mode === 'manual') {
        mapContainer.style.display = 'none';
        manualContainer.style.display = 'block';
        drawnItems.clearLayers();
    } else {
        mapContainer.style.display = 'block';
        manualContainer.style.display = 'none';

        setTimeout(() => {
            map.invalidateSize();
            map.setView(map.getCenter(), map.getZoom(), {animate: false});

            if (coordinates.length > 0) {
                L.polygon(coordinates, {
                    color: '#3388ff',
                    fillOpacity: 0.4
                }).addTo(drawnItems);
            }
        }, 50);
    }
}

function parseManualCoords() {
    const input = document.getElementById('manual-coordinates').value.trim();
    const errorDiv = document.getElementById('error-message');

    try {
        coordinates = input.split('\n')
            .filter(line => line.trim())
            .map(line => {
                const [lat, lon] = line.split(',').map(Number);
                if (isNaN(lat) || isNaN(lon)) throw new Error();
                return [lat, lon];
            });

        if (coordinates.length < 3) throw new Error('Необходимо минимум 3 точки');
        if (coordinates[0][0] !== coordinates[coordinates.length-1][0] ||
            coordinates[0][1] !== coordinates[coordinates.length-1][1]) {
            coordinates.push(coordinates[0]);
        }

        drawnItems.clearLayers();
        const polygon = L.polygon(coordinates, {
            color: '#3388ff',
            fillOpacity: 0.4
        }).addTo(drawnItems);

        const area = turf.area(polygon.toGeoJSON());
        updateArea(area / 10000);
        errorDiv.style.display = 'none';
    } catch (e) {
        errorDiv.textContent = e.message || 'Некорректный формат координат';
        errorDiv.style.display = 'block';
    }
}

async function saveField() {
    const errorDiv = document.getElementById('error-message');
    errorDiv.textContent = '';
    errorDiv.style.display = 'none';

    try {
        if (!document.getElementById('field-name').value) throw new Error('Укажите название поля');
        if (coordinates.length < 3) throw new Error('Необходимо указать полигон');

        const fieldData = {
            name: document.getElementById('field-name').value,
            field_number: document.getElementById('field-number').value,
            soil_type: document.getElementById('soil-type').value,
            coordinates: coordinates.slice(0, -1).map(c => ({ lat: c[0], lon: c[1] })),
            area: document.getElementById('area').value
        };

        const response = await fetch('/fields/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${getCookie('users_access_token')}`
            },
            body: JSON.stringify(fieldData)
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Ошибка сервера');
        }

        window.location.href = '/pages/my_fields';
    } catch (error) {
        errorDiv.textContent = error.message;
        errorDiv.style.display = 'block';
    }
}

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}

document.addEventListener('DOMContentLoaded', initMap);
