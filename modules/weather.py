#keys
import os
import requests
import json

#----------------- LOCAL TESTING -----------------#
# import config
# OPENWEATHERMAP_KEY = config.OPENWEATHERMAP_KEY
#-------------------------------------------------#

#----------------- DEPLOYMENT -----------------#
OPENWEATHERMAP_KEY = os.environ.get('OPENWEATHERMAP_KEY')
#-------------------------------------------------#




def get_lat_long(city: str):
    url = "https://nominatim.openstreetmap.org/search?q="+city+"&format=json&limit=1"

    response = requests.get(url).text
    parsed_data = json.loads(response)
    for data in parsed_data:
        lat = data['lat']
        long = data['lon']
    return lat, long

def get_weather(city: str):
    lat, long = get_lat_long(city)

    #wetter now
    url_now = "https://api.openweathermap.org/data/2.5/weather?lat="+lat+"&lon="+long+"&appid="+OPENWEATHERMAP_KEY+"&units=metric&lang=de"
    response_now = requests.get(url_now).text
    parsed_data_now = json.loads(response_now)

    #wetter forecast
    url_forecast = "https://api.openweathermap.org/data/2.5/forecast?lat="+lat+"&lon="+long+"&appid="+OPENWEATHERMAP_KEY+"&units=metric&lang=de"
    response_forecast = requests.get(url_forecast).text
    parsed_data_forecast = json.loads(response_forecast)
    weather = {
        "city": parsed_data_now["name"],
        "weather": parsed_data_now["weather"][0]["description"],
        "icon": parsed_data_now["weather"][0]["icon"],
        "temp": parsed_data_now["main"]["temp"],
        "feels_like": parsed_data_now["main"]["feels_like"],
        "temp_min": parsed_data_now["main"]["temp_min"],
        "temp_max": parsed_data_now["main"]["temp_max"],
        "humidity": parsed_data_now["main"]["humidity"],
        "wind_speed": parsed_data_now["wind"]["speed"],
        "forecast": [        
            {            
                "date": parsed_data_forecast["list"][8]["dt"],
                "weather": parsed_data_forecast["list"][8]["weather"][0]["description"],
                "icon": parsed_data_forecast["list"][8]["weather"][0]["icon"],
                "temp": parsed_data_forecast["list"][8]["main"]["temp"],
                "humidity": parsed_data_forecast["list"][8]["main"]["humidity"],
                "wind_speed": parsed_data_forecast["list"][8]["wind"]["speed"],
            },
            {
                "date": parsed_data_forecast["list"][16]["dt"],
                "weather": parsed_data_forecast["list"][16]["weather"][0]["description"],
                "icon": parsed_data_forecast["list"][16]["weather"][0]["icon"],
                "temp": parsed_data_forecast["list"][16]["main"]["temp"],
                "humidity": parsed_data_forecast["list"][16]["main"]["humidity"],
                "wind_speed": parsed_data_forecast["list"][16]["wind"]["speed"],

            },
            {
                "date": parsed_data_forecast["list"][24]["dt"],
                "weather": parsed_data_forecast["list"][24]["weather"][0]["description"],
                "icon": parsed_data_forecast["list"][24]["weather"][0]["icon"],
                "temp": parsed_data_forecast["list"][24]["main"]["temp"],
                "humidity": parsed_data_forecast["list"][24]["main"]["humidity"],
                "wind_speed": parsed_data_forecast["list"][24]["wind"]["speed"],

            },
            {
                "date": parsed_data_forecast["list"][32]["dt"],
                "weather": parsed_data_forecast["list"][32]["weather"][0]["description"],
                "icon": parsed_data_forecast["list"][32]["weather"][0]["icon"],
                "temp": parsed_data_forecast["list"][32]["main"]["temp"],
                "humidity": parsed_data_forecast["list"][32]["main"]["humidity"],
                "wind_speed": parsed_data_forecast["list"][32]["wind"]["speed"],

            },
            {
                "date": parsed_data_forecast["list"][39]["dt"],
                "weather": parsed_data_forecast["list"][39]["weather"][0]["description"],
                "icon": parsed_data_forecast["list"][39]["weather"][0]["icon"],
                "temp": parsed_data_forecast["list"][39]["main"]["temp"],
                "humidity": parsed_data_forecast["list"][39]["main"]["humidity"],
                "wind_speed": parsed_data_forecast["list"][39]["wind"]["speed"],

            },
        ],
    }

    return weather