# Файл для первого задания

from flask import Flask, request, jsonify
import requests
import json
from api import API_KEY

app = Flask(__name__)

# Основной URL для API запросов к AccuWeather
BASE_URL = "http://dataservice.accuweather.com"


# Функция для получения location_key по координатам
def get_location_key(lat, lon):
    weather_url = f"{BASE_URL}/locations/v1/cities/geoposition/search?apikey={API_KEY}&q={lat}%2C{lon}&language=en-us&details=true&toplevel=false"

    loc_data = requests.get(weather_url)
    loc_data = loc_data.json()
    loc_key = loc_data['Key']

    return int(loc_key)

# Функция для получения данных о погоде по координатам
def get_weather_data(location_key):

    # Запрос для получения прогноза погоды по locationKey
    weather_url = f"{BASE_URL}/forecasts/v1/daily/1day/{location_key}?apikey={API_KEY}&language=en-us&details=true&metric=true"
    response = requests.get(weather_url)

    if response.status_code != 200:
        return {"error": "Не удалось получить данные о погоде"}

    # Возвращаем JSON данные
    return response.json()

# Главная страница
@app.route('/')
def home():
    return '''
        <h1>Weather Forecast Service</h1>
        <p>Введите координаты (широта и долгота) для получения прогноза погоды.</p>
        <form action="/weather" method="get">
            <label for="lat">Широта:</label><br>
            <input type="text" id="lat" name="lat"><br>
            <label for="lon">Долгота:</label><br>
            <input type="text" id="lon" name="lon"><br><br>
            <input type="submit" value="Получить прогноз">
        </form>
    '''

# Маршрут для получения прогноза погоды
@app.route('/weather', methods=['GET'])
def weather():
    # Получаем широту и долготу из параметров запроса
    latitude = request.args.get('lat')
    longitude = request.args.get('lon')

    if not latitude or not longitude:
        return jsonify({"error": "Укажите широту и долготу!"})

    # Получаем данные о погоде
    location_key = get_location_key(latitude, longitude) #получаем его с сайта для широта и долготы: 35.113320, 101.484582
    weather_data = get_weather_data(location_key)

    # Если произошла ошибка при получении данных
    if "error" in weather_data:
        return jsonify(weather_data)

    # Пример извлечения ключевых данных
    forecast = weather_data['DailyForecasts'][0]
    mx_temperature = forecast['Temperature']['Maximum']['Value']
    mn_temperature = forecast['Temperature']['Minimum']['Value']
    wind_speed = forecast['Day']['Wind']['Speed']['Value']
    rain_probability = forecast['Day']['PrecipitationProbability']
    relative_humidity = forecast['Day']['RelativeHumidity']['Average']

    # Формируем и возвращаем данные пользователю
    return jsonify({
        "location": f"Координаты: {latitude}, {longitude}",
        "temperature_max": f"Максимальная температура: {mx_temperature} °C",
        "temperature_min": f"Минимальная температура: {mn_temperature} °C",
        "wind_speed": f"Скорость ветра: {wind_speed} км/ч",
        "rain_probability": f"Вероятность осадков: {rain_probability} %",
        "relative_humidity": f"Влажность: {relative_humidity} %"
    })

# Запуск сервера
if __name__ == '__main__':
    app.run(debug=True)
