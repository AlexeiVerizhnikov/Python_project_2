from flask import Flask, request, render_template, jsonify
import requests
from api import API_KEY
app = Flask(__name__)

BASE_URL = "http://dataservice.accuweather.com"

# Функция для проверки неблагоприятности погодных условий
def check_bad_weather(mn_t, mx_t, wind_speed, rain_prob):
    if mn_t < 0 or mx_t > 35:
        return "Температура экстремальна!"
    if wind_speed > 50:
        return "Сильный ветер!"
    if rain_prob > 70:
        return "Высокая вероятность осадков!"
    return "Погода благоприятная."

# Функция для получения location_key по координатам
def get_location_key(lat, lon):
    weather_url = f"{BASE_URL}/locations/v1/cities/geoposition/search?apikey={API_KEY}&q={lat}%2C{lon}"
    try:
        loc_data = requests.get(weather_url)
        loc_data = loc_data.json()
        loc_key = loc_data['Key']
        return loc_key
    except Exception as e:
        return render_template('index.html', error = "Недоступные данные ключа")

# Функция для получения данных о погоде по координатам
def get_weather_data(location_key):
    weather_url = f"{BASE_URL}/forecasts/v1/daily/1day/{location_key}?apikey={API_KEY}&language=en-us&details=true&metric=true"
    try:
        response = requests.get(weather_url)
        if response.status_code != 200:
            return None
        return response.json()
    except Exception as e:
        return render_template('index.html', error = "Недоступные данные погоды")

# Главная страница
@app.route('/')
def home():
    return render_template('index.html')

# Маршрут для получения прогноза погоды
@app.route('/weather', methods=['POST'])
def weather():
    # Получаем данные из формы
    st_latitude = request.form['lat_st']
    st_longitude = request.form['lon_st']
    end_latitude = request.form['lat_end']
    end_longitude = request.form['lon_end']

    # Проверка, что все поля заполнены
    if not st_latitude or not st_longitude or not end_latitude or not end_longitude:
        return "Ошибка: Укажите все координаты!", 400

    # Получаем location_key для начальной точки
    location_key_st = get_location_key(st_latitude, st_longitude)
    if not location_key_st:
        return "Ошибка: Не удалось найти начальную точку!", 400

    # Получаем location_key для конечной точки
    location_key_end = get_location_key(end_latitude, end_longitude)
    if not location_key_end:
        return "Ошибка: Не удалось найти конечную точку!", 400

    # Получаем данные о погоде для начальной и конечной точек
    weather_data_st = get_weather_data(location_key_st)
    weather_data_end = get_weather_data(location_key_end)

    if not weather_data_st or not weather_data_end:
        return "Ошибка: Не удалось получить данные о погоде!", 400

    # Извлекаем ключевые данные для начальной точки
    forecast_st = weather_data_st['DailyForecasts'][0]
    mx_temperature_st = forecast_st['Temperature']['Maximum']['Value']
    mn_temperature_st = forecast_st['Temperature']['Minimum']['Value']
    wind_speed_st = forecast_st['Day']['Wind']['Speed']['Value']
    rain_prob_st = forecast_st['Day']['PrecipitationProbability']

    # Извлекаем ключевые данные для конечной точки
    forecast_end = weather_data_end['DailyForecasts'][0]
    mx_temperature_end = forecast_end['Temperature']['Maximum']['Value']
    mn_temperature_end = forecast_end['Temperature']['Minimum']['Value']
    wind_speed_end = forecast_end['Day']['Wind']['Speed']['Value']
    rain_prob_end = forecast_end['Day']['PrecipitationProbability']

    # Проверяем погодные условия для начальной и конечной точек
    weather_report_st = check_bad_weather(mn_temperature_st, mx_temperature_st, wind_speed_st, rain_prob_st)
    weather_report_end = check_bad_weather(mn_temperature_end, mx_temperature_end, wind_speed_end, rain_prob_end)

    # Возвращаем результат пользователю
    return f'''
        <h2>Прогноз для начальной точки:</h2>
        <p>{weather_report_st}</p>
        <h2>Прогноз для конечной точки:</h2>
        <p>{weather_report_end}</p>
        <a href="/">Назад</a>
    '''

# Запуск сервера
if __name__ == '__main__':
    app.run(debug=True)
