import requests
import json
import config

OPENWEATHERMAP_KEY = config.OPENWEATHERMAP_KEY


def get_lat_long(city: str):
    url = "https://nominatim.openstreetmap.org/search?q="+city+"&format=json&limit=1"

    response = requests.get(url).text
    parsed_data = json.loads(response)
    for data in parsed_data:
        lat = data['lat']
        long = data['lon']
    return lat, long

def get_weather(city: str):
    lat, lon = get_lat_long(city)
    url = "https://api.openweathermap.org/data/2.5/weather?lat="+lat+"&lon="+lon+"&appid="+OPENWEATHERMAP_KEY
    response = requests.get(url).text
    parsed_data = json.loads(response)
    return parsed_data