import openai
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import json
import config
import uuid
import requests

OPEN_AI_KEY = config.OPEN_AI_KEY
PIXABAY_KEY = config.PIXABAY_KEY
cred = credentials.Certificate(".env/firebase_key.json")
placeholder_img = "https://pixabay.com/get/g3ea5c0ed6d9e4188af3264388e236188a0e2785f78d7d8d530b2dcb19e94a7e19ef01b6899578d6c5f76399f88c4a3d70e28f016267a7d9463c029aec451103a_640.jpg"

firebase_admin.initialize_app(cred)

def plantlookup(name: str):
    #search for Plant in Firestore
    db = firestore.client()
    docs = db.collection('plants').where('common_name', '==', name).get()

    #if plant is in the database
    if len(docs) > 0:
        plant = docs[0].to_dict()
        return plant
    #if plant is nowhere in the database
    else:
        plant = generate_new_plant(name)
        return plant
    

def generate_new_plant(name: str):
    #generate and upload new plant data
    plant = {
        "id": uuid.uuid4().hex,
        "common_name": name,
    }
    prompt = 'Liefere mir ein Array mit Daten über: \n ' + name + '\n mit den Informationen: \n {"scientific_name": latein \n "description": maximal drei Sätze \n "harvest": Ein Wort aus Frühling, Sommer, Herbst, Winter \n "sun": ganzzahliger Wert zwischen 0 und 10 \n "water": ganzzahliger Wert zwischen 0 und 10 \n "ph": ganzzahliger Wert zwischen 0 und 14 \n "companion_plants": Aufzählung von Pflanzennamen getrennt mit einem Komma} \n Beachte die Formatierungsvorgaben nach dem jeweiligen Doppelpunkt. \n Gibt es mehrere Pflanzen mit dieser Bezeichnung wähle die am weitesten verbreitete aus. \n Liefere mir nur das Array und keine weiteren Informationen oder Text zurück.'
    ai_response = request_open_ai(prompt)
    # parse the API response as a dictionary
    api_dict = json.loads(ai_response.replace('\n', '').replace('[', '').replace(']', ''))
    companion_plants = api_dict.get("companion_plants").split(',')

    # update the plant dictionary with the API data
    plant.update({
        "scientific_name": api_dict.get("scientific_name"),
        "description": api_dict.get("description"),
        "harvest": api_dict.get("harvest"),
        "sun": api_dict.get("sun"),
        "water": api_dict.get("water"),
        "ph": api_dict.get("ph"),
        "companion_plants": companion_plants
    })

    #get plant image
    plant["image"] = plant_image(name)

    #push to firebase
    push_plant_to_firebase(plant["id"], plant)
    return plant

def request_open_ai(text: str):
    openai.api_key = OPEN_AI_KEY
    response = openai.Completion.create(model="text-davinci-003", prompt=text, temperature=0.5, max_tokens=1000)

    return response["choices"][0]["text"]

def plant_image(name):
    #search for plant image via pixabay API
    url="https://pixabay.com/api/?key="+PIXABAY_KEY+"&q="+name+"&image_type=photo&category=nature&per_page=3"
    response = requests.get(url).text
    parsed_data = json.loads(response)
    if len(parsed_data["hits"]) > 0:
        img_url = parsed_data["hits"][0]["webformatURL"]
        return img_url
    else:
        return placeholder_img


def push_plant_to_firebase(id, plant):
    db = firestore.client()

    # Add the new document to the "plants" collection
    doc_ref = db.collection('plants').document(str(id))
    doc_ref.set(plant)
    return "success"