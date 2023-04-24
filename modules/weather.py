import requests
import json
#import config

OPENWEATHERMAP_KEY = "123"#config.OPENWEATHERMAP_KEY


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
    url_forecast = "https://api.openweathermap.org/data/2.5/forecast?lat="+lat+"&lon="+long+"&appid="+OPENWEATHERMAP_KEY+"&units=metric&lang=de&cnt=5"
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
                "date": parsed_data_forecast["list"][0]["dt"],
                "weather": parsed_data_forecast["list"][0]["weather"][0]["description"],
                "icon": parsed_data_forecast["list"][0]["weather"][0]["icon"],
                "temp": parsed_data_forecast["list"][0]["main"]["temp"],
                "humidity": parsed_data_forecast["list"][0]["main"]["humidity"],
            },
            {
                "date": parsed_data_forecast["list"][1]["dt"],
                "weather": parsed_data_forecast["list"][1]["weather"][0]["description"],
                "icon": parsed_data_forecast["list"][1]["weather"][0]["icon"],
                "temp": parsed_data_forecast["list"][1]["main"]["temp"],
                "humidity": parsed_data_forecast["list"][1]["main"]["humidity"],
            },
            {
                "date": parsed_data_forecast["list"][2]["dt"],
                "weather": parsed_data_forecast["list"][2]["weather"][0]["description"],
                "icon": parsed_data_forecast["list"][2]["weather"][0]["icon"],
                "temp": parsed_data_forecast["list"][2]["main"]["temp"],
                "humidity": parsed_data_forecast["list"][2]["main"]["humidity"],
            },
            {
                "date": parsed_data_forecast["list"][3]["dt"],
                "weather": parsed_data_forecast["list"][3]["weather"][0]["description"],
                "icon": parsed_data_forecast["list"][3]["weather"][0]["icon"],
                "temp": parsed_data_forecast["list"][3]["main"]["temp"],
                "humidity": parsed_data_forecast["list"][3]["main"]["humidity"],
            },
            {
                "date": parsed_data_forecast["list"][4]["dt"],
                "weather": parsed_data_forecast["list"][4]["weather"][0]["description"],
                "icon": parsed_data_forecast["list"][4]["weather"][0]["icon"],
                "temp": parsed_data_forecast["list"][4]["main"]["temp"],
                "humidity": parsed_data_forecast["list"][4]["main"]["humidity"],
            },
        ],
    }

    return weather