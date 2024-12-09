from flask import Flask, request, render_template
import requests
from api import API_KEY

app = Flask(__name__)

API_BASE_URL = "http://dataservice.accuweather.com"

def assess_weather_conditions(min_temp, max_temp, wind_speed, precipitation_chance):
    if min_temp < 0 or max_temp > 35:
        return "Температура экстремальна!"
    if wind_speed > 50:
        return "Сильный ветер!"
    if precipitation_chance > 70:
        return "Высокая вероятность осадков!"
    return "Погода благоприятная."

def fetch_location_key(latitude, longitude):
    url = f"{API_BASE_URL}/locations/v1/cities/geoposition/search?apikey={API_KEY}&q={latitude}%2C{longitude}"
    response = requests.get(url)
    
    if response.ok:
        return response.json().get('Key')
    return None

def fetch_weather_info(location_key):
    url = f"{API_BASE_URL}/forecasts/v1/daily/1day/{location_key}?apikey={API_KEY}&language=en-us&details=true&metric=true"
    response = requests.get(url)
    
    if response.ok:
        return response.json()
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/weather', methods=['POST'])
def weather_forecast():
    start_lat = request.form['lat_st']
    start_lon = request.form['lon_st']
    end_lat = request.form['lat_end']
    end_lon = request.form['lon_end']

    if not all([start_lat, start_lon, end_lat, end_lon]):
        return "Ошибка: Укажите все координаты!", 400

    start_location_key = fetch_location_key(start_lat, start_lon)
    if not start_location_key:
        return "Ошибка: Не удалось найти начальную точку!", 400

    end_location_key = fetch_location_key(end_lat, end_lon)
    if not end_location_key:
        return "Ошибка: Не удалось найти конечную точку!", 400

    start_weather_info = fetch_weather_info(start_location_key)
    end_weather_info = fetch_weather_info(end_location_key)

    if not start_weather_info or not end_weather_info:
        return "Ошибка: Не удалось получить данные о погоде!", 400

    start_forecast = start_weather_info['DailyForecasts'][0]
    end_forecast = end_weather_info['DailyForecasts'][0]

    start_report = assess_weather_conditions(
        start_forecast['Temperature']['Minimum']['Value'],
        start_forecast['Temperature']['Maximum']['Value'],
        start_forecast['Day']['Wind']['Speed']['Value'],
        start_forecast['Day']['PrecipitationProbability']
    )

    end_report = assess_weather_conditions(
        end_forecast['Temperature']['Minimum']['Value'],
        end_forecast['Temperature']['Maximum']['Value'],
        end_forecast['Day']['Wind']['Speed']['Value'],
        end_forecast['Day']['PrecipitationProbability']
    )

    return f'''
        <h2>Прогноз для начальной точки:</h2>
        <p>{start_report}</p>
        <h2>Прогноз для конечной точки:</h2>
        <p>{end_report}</p>
        <a href="/">Назад</a>
    '''

if __name__ == '__main__':
    app.run(debug=True)
