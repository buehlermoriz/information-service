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
firebase_admin.initialize_app(cred)

def request_open_ai(text: str, model: str, temp: float, max_tokens: int):
    openai.api_key = OPEN_AI_KEY
    response = openai.Completion.create(model=model, prompt=text, temperature=temp, max_tokens=max_tokens)

    return response["choices"][0]["text"]


def push_plant_to_firebase(id, common_name, scientific_name, img_url, synonyms, family):
    db = firestore.client()
 # Define the data for the new plant document
    data = {
        'id': id,
        'common_name': common_name,
        'scientific_name': scientific_name,
        'img_url': img_url,
        'synonyms': synonyms,
        'family': family
    }

    # Add the new document to the "plants" collection
    doc_ref = db.collection('plants').document(str(id))
    doc_ref.set(data)
    return "success"

def plantlookup(name: str):
    url = "https://trefle.io/api/v1/species/search?q=" + name + "&token=" + TREFLE_KEY
    response = requests.get(url).text
    parsed_data = json.loads(response)
    for plant in parsed_data['data']:
        push_plant_to_firebase(plant["id"], plant["common_name"], plant["scientific_name"], plant["image_url"], plant["synonyms"], plant["family"])
    plant= response["data"][0]

    return plant