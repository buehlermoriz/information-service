#keys
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import json
import uuid
import requests
from google.cloud import storage
from google.oauth2 import service_account
from datetime import datetime, timedelta
from modules import openai

#----------------- LOCAL TESTING -----------------#
# cred = credentials.Certificate("env/firebase_key.json")
# storage_client = storage.Client.from_service_account_json("env/firebase_key.json")
#-------------------------------------------------#

#----------------- DEPLOYMENT -----------------#
import os
FIREBASE_KEY = {
   "type": "service_account",
   "project_id":"lumela-2fb04",
   "private_key_id": os.environ.get('private_key_id'),
   "private_key": os.environ.get('private_key').replace("\\n", "\n"),
  "client_email": "firebase-adminsdk-p8yj1@lumela-2fb04.iam.gserviceaccount.com",
  "client_id": "109723090998767991936",
   "auth_uri": "https://accounts.google.com/o/oauth2/auth",
   "token_uri": "https://oauth2.googleapis.com/token",
   "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
   "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-p8yj1%40lumela-2fb04.iam.gserviceaccount.com"
 }
cred = credentials.Certificate(FIREBASE_KEY)
credentials = service_account.Credentials.from_service_account_info(FIREBASE_KEY)
storage_client = storage.Client(credentials=credentials)
#-------------------------------------------------#

firebase_admin.initialize_app(cred)
bucket = storage_client.get_bucket('lumela-2fb04.appspot.com')


def plant_lookup(name: str):
    #search for Plant in Firestore
    db = firestore.client()
    docs = db.collection('plants').where('common_name', '==', name).get()

    #if plant is in the database
    if len(docs) > 0:
        plant = docs[0].to_dict()
        plant = check_if_url_expired(plant)
        return plant
    #if plant is nowhere in the database
    else:
        plant = generate_new_plant(name)
        return plant
    
def plant_list_lookup(names: list):
    #search for Plant in Firestore
    db = firestore.client()
    
    # perform a query for all plants matching the common names
    docs = db.collection('plants').where('id', 'in', names).get()

    #if plant is in the database
    if len(docs) > 0:
        plants = [doc.to_dict() for doc in docs]
        for plant in plants:
            plant = check_if_url_expired(plant)
        return plants
    #if plant is nowhere in the database
    else:
        return "ERROR - info_service - plants.py - plant_list_lookup: Die angefragten Pflanzen ("+str(names)+") einer der angefragten Beete existieren nicht! Wahrschienlich wurden diese manuell gelöscht. Bitte werfe einen Blick in den Firestore, oder melde dich bei mir (Moriz)", 400
    
def all_plants():
    #search for Plant in Firestore
    db = firestore.client()
    
    # perform a query for all plants matching the common names
    docs = db.collection('plants').get()

    #if plant is in the database
    if len(docs) > 0:
        plants = [doc.to_dict() for doc in docs]
        for plant in plants:
            plant = check_if_url_expired(plant)
        return plants
    #if plant is nowhere in the database
    else:
        return "plants not found", 400
    

def generate_new_plant(name: str, id: str = None):
    #check if request is from reload plant. If it is from relaod plant, the provided id is used
    if id:
        plant_id = id
    else:
        plant_id = uuid.uuid4().hex
    #generate and upload new plant data
    plant = {
        "id": plant_id,
        "common_name": name,
    }
    prompt = 'Liefere mir ein Array mit Daten über: \n ' + name + '\n mit den Informationen: \n {"scientific_name": latein \n "description": maximal drei Sätze \n "harvest": Ein Wort aus Frühling, Sommer, Herbst, Winter \n "sun": ganzzahliger Wert zwischen 0 und 5 \n "water": ganzzahliger Wert zwischen 0 und 5 \n "ph": ganzzahliger Wert zwischen 0 und 14 \n "companion_plants": Aufzählung von Pflanzennamen getrennt mit einem Komma \n "toxic_level": wert zwischen 0 und 4 (0=nicht giftig, 1= wenig giftig, 2= gifitig, 3=stark giftig, 4=sehr stark gifitg) \n "taste": Wähle zwischen den Geschmacksrichtungen Umami, Süß, Sauer, Salzig, Bitter} \n Beachte die Formatierungsvorgaben nach dem jeweiligen Doppelpunkt. \n Gibt es mehrere Pflanzen mit dieser Bezeichnung wähle die am weitesten verbreitete aus. \n Liefere mir nur das Array und keine weiteren Informationen oder Text zurück.'
    ai_response = openai.request_open_ai(prompt)
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
        "toxic_level": api_dict.get("toxic_level"),
        "taste": api_dict.get("taste"),
        "companion_plants": companion_plants
    })

    #get plant image
    image_url, plant_img = openai.request_open_ai_image(name)
    plant["firebase_path"], plant["img"] = upload_image(image_url, plant_img)
    #push to firebase
    upload_plant(plant["id"], plant)
    return plant

def upload_plant(id, plant):
    db = firestore.client()

    #Add the new document to the "plants" collection
    doc_ref = db.collection('plants').document(str(id))
    doc_ref.set(plant)
    return "success"

def upload_image(image_url, plant):
    #get the image from the url
    response = requests.get(image_url)
    #upload image to firebase storage
    blob = bucket.blob("plantimages/"+plant)
    blob.upload_from_string(response.content, content_type=response.headers['content-type'])
    url = blob.generate_signed_url(expiration=86400, version="v4")
    return "plantimages/"+plant, url

def check_if_url_expired(plant):
    url = plant["img"]
    upload_date = url.split("X-Goog-Date=")[-1].split("&")[0]
    date_fmt = "%Y%m%dT%H%M%SZ"
    expires = int(url.split("X-Goog-Expires=")[-1].split("&")[0])

    expires_at = datetime.strptime(upload_date, date_fmt) + timedelta(seconds=expires)

    if datetime.utcnow() >= expires_at:
        # generate new URL
        blob = bucket.blob(plant["firebase_path"])
        url = blob.generate_signed_url(expiration=86400, version="v4")
        plant["img"] = url
        return plant
    else:
        return plant
