import openai
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import requests
import config
import json

OPEN_AI_KEY = config.OPEN_AI_KEY
cred = credentials.Certificate(".env/firebase_key.json")
TREFLE_KEY = config.TREFLE_KEY
OPENWEATHERMAP_KEY = config.OPENWEATHERMAP_KEY

firebase_admin.initialize_app(cred)

def request_open_ai(text: str):
    openai.api_key = OPEN_AI_KEY
    response = openai.Completion.create(model="text-davinci-003", prompt=text, temperature=0.5, max_tokens=1000)

    return response["choices"][0]["text"]


def push_plant_to_firebase(id, common_name, scientific_name, img_url):
    db = firestore.client()
 # Define the data for the new plant document
    data = {
        'id': id,
        'common_name': common_name,
        'scientific_name': scientific_name,
        'img_url': img_url,
    }

    # Add the new document to the "plants" collection
    doc_ref = db.collection('plants').document(str(id))
    doc_ref.set(data)
    return "success"

def plantlookup(name: str):
    url = "https://trefle.io/api/v1/species/search?q=" + name +"&token=" + TREFLE_KEY
    response = requests.get(url).text
    parsed_data = json.loads(response)
    first_response = parsed_data["data"][0]
    plant = {
        "id": first_response["id"],
        "common_name": first_response["common_name"],
        "scientific_name": first_response["scientific_name"],
        "image_url": first_response["image_url"],
    }
    prompt = "Übersetze den folgenden Eintrag auf deutsch. Behalte die Formatierung bei. Ergänze die Information, mit welchen anderen Pflanzen die Planze gut zusammen wächst:" + str(plant)
    ai_response = request_open_ai(prompt)
    #push to firebase
    #push_plant_to_firebase(plant["id"], plant["common_name"], plant["scientific_name"], plant["image_url"])

    return plant

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
    url = "https://api.openweathermap.org/data/2.5/weather?lat="+lat+"&lon="+lon+"&appid=2d55c039196e807f27ea4b14fda8d789"
    response = requests.get(url).text
    parsed_data = json.loads(response)
    return parsed_data