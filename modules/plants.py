#keys
import openai
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import json
import uuid
import requests
from google.cloud import storage
from datetime import datetime, timedelta

#----------------- LOCAL TESTING -----------------#
# import config
# OPEN_AI_KEY = config.OPEN_AI_KEY
# cred = credentials.Certificate("env/firebase_key.json")
# storage_client = storage.Client.from_service_account_json("env/firebase_key.json")
#-------------------------------------------------#

#----------------- DEPLOYMENT -----------------#
import os
OPEN_AI_KEY = os.environ.get('OPEN_AI_KEY')
FIREBASE_KEY = {
   "type": "service_account",
   "project_id": os.environ.get('project_id'),
   "private_key_id": os.environ.get('private_key_id'),
   "private_key": os.environ.get('private_key').replace("\\n", "\n"),
   "client_email": os.environ.get('client_email'),
   "client_id": os.environ.get('client_id'),
   "auth_uri": "https://accounts.google.com/o/oauth2/auth",
   "token_uri": "https://oauth2.googleapis.com/token",
   "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
   "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-p8yj1%40lumela-2fb04.iam.gserviceaccount.com"
 }
cred = credentials.Certificate(FIREBASE_KEY)
#storage_client = storage.Client.from_service_account_json(FIREBASE_KEY)
#-------------------------------------------------#

firebase_admin.initialize_app(cred)
#bucket = storage_client.get_bucket('lumela-2fb04.appspot.com')


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
        return "plants not found", 400
    

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
    plant["firebase_path"], plant["img"] = request_open_ai_image(name)
    #push to firebase
    upload_plant(plant["id"], plant)
    return plant

def request_open_ai(text: str):
    openai.api_key = OPEN_AI_KEY
    response = openai.Completion.create(model="text-davinci-003", prompt=text, temperature=0.5, max_tokens=1000)

    return response["choices"][0]["text"]

def request_open_ai_image(plant: str):
    ai_prompt = "Eine" + plant + "in einem Garten bei gutem Wetter kurz nachdem es geregnet hat wobei die Pflanze von den ersten Sonnenstrahlen getroffen wird."
    openai.api_key = OPEN_AI_KEY
    response = openai.Image.create(
    prompt=ai_prompt,
    n=1,
    size="1024x1024"
    )
    image_url = response['data'][0]['url']
    firebase_path = upload_image(image_url, plant)
    return firebase_path

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
    # blob = bucket.blob("plantimages/"+plant)
    # blob.upload_from_string(response.content, content_type=response.headers['content-type'])
    # url = blob.generate_signed_url(expiration=86400, version="v4")
    url = "https://storage.googleapis.com/lumela-2fb04.appspot.com/plantimages/Kirsche?X-Goog-Algorithm=GOOG4-RSA-SHA256&X-Goog-Credential=firebase-adminsdk-p8yj1%40lumela-2fb04.iam.gserviceaccount.com%2F20230427%2Fauto%2Fstorage%2Fgoog4_request&X-Goog-Date=20230427T063328Z&X-Goog-Expires=86400&X-Goog-SignedHeaders=host&X-Goog-Signature=8925a110b8b5168b530500c13e11f9d273cba0b30efdabf6d5ede6deb0b01f57d91caf78f8611803cdca4093151898dfe6cd06c250eb9febf33c27dc636ddf5551587633ec0e4d11aad8f635e5426edd85e553ef217aeb5d4448b7413a7fc97c51b83aefe6d4f343980e9692f9e221fc670c55e8d01c22359f926ac2200ffcdfb0c6647a0a402e2fb440f561afb829fe828e1a83158e155b20c2c985736cbd45786b1caf096705564d2a2f0697060ecab161cde0ae240797b9003512a2fbc1a6e474e0e92d41105dc46d387f2d21df68d8540d8316bc066a5a08d9d0d900b98fc6e3c69f1a9c835690a89f1903aad60602be8f912dd1290d6902061ed14118de"
    return "plantimages/"+plant, url

def check_if_url_expired(plant):
    url = plant["img"]
    upload_date = url.split("X-Goog-Date=")[-1].split("&")[0]
    date_fmt = "%Y%m%dT%H%M%SZ"
    expires = int(url.split("X-Goog-Expires=")[-1].split("&")[0])

    expires_at = datetime.strptime(upload_date, date_fmt) + timedelta(seconds=expires)

    if datetime.utcnow() >= expires_at:
        # generate new URL
        # blob = bucket.blob(plant["firebase_path"])
        # url = blob.generate_signed_url(expiration=86400, version="v4")
        # plant["img"] = url
        return plant
    else:
        return plant
