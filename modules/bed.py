#keys
from firebase_admin import credentials
import json
from google.cloud import storage
from modules import openai
import re 
import json
from google.oauth2 import service_account


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

def find_companion_plants(light, water, plantIds, soil, time, alignment):
    #AI Rrequest
    prompt = generate_create_prompt(light, water, plantIds, soil, time, alignment)
    ai_response = openai.request_open_ai(prompt)
    # parse the API response as an array
    array_str = re.search('\[.*\]', ai_response).group()
    array = json.loads(array_str)
    return array

def check_plant_compatibility(light, water, soil, time, alignment, plant_names, check_plant_name):
    #AI Rrequest
    prompt = generate_check_prompt(light, water, plant_names, soil, time, alignment, check_plant_name)
    ai_response = openai.request_open_ai(prompt)
    # parse the API response as an array
    array_str = re.search('\[.*\]', ai_response).group()
    array = json.loads(array_str)
    return array

def generate_create_prompt(light, water, plant_names_str, soil, time, alignment):

    light_levels = {
    0: 'nicht',
    1: 'kaum',
    2: 'wenig',
    3: 'einigermaßen',
    4: 'sehr',
    5: 'sehr sehr'
    }
    water_levels = {
    0: 'kein',
    1: 'kaum',
    2: 'wenig',
    3: 'eine gute Menge an',
    4: 'viel',
    5: 'sehr viel'
    }
    work_levels = {
    'Niedrig': 'wenig',
    'Mittel': 'mittelmäßig viel',
    'Hoch': 'sehr viel',
    }
    light_lv = light_levels.get(light, 'unbekannt')
    water_lv = water_levels.get(water, 'unbekannt')
    time_lv = work_levels.get(time, 'unbekannt')

    
    prompt = 'Ich plane ein neues Gartenbeet und suche Pflanzen, welche ich darin anbauen kann. Wo das Beet aufgebaut wird ist es '+light_lv+' sonnig. Das Beet ist in Richtung '+alignment+' ausgerichtet. Für die Versorgung des Beets habe ich '+water_lv+' Wasser zur Verfügung. Auf jeden Fall will ich folgende Pflanzen in meinem Beet anbauen: '+plant_names_str+'. Der Boden in meinem besteht aus viel '+soil+'. Ich habe für mein Beet '+time_lv+' Zeit. Bitte liefere mir ein array mit dem Namen "pflanzen" für die Verarbeitung in Python mit 10 weiteren Pflanzen, welche ich anhand der gegebenen Parameter in meinem Beet anbauen sollte.'

    return prompt

def generate_check_prompt(light, water, plant_names_str, soil, time, alignment, check_plant_name):

    light_levels = {
    0: 'nicht',
    1: 'kaum',
    2: 'wenig',
    3: 'einigermaßen',
    4: 'sehr',
    5: 'sehr sehr'
    }
    water_levels = {
    0: 'kein',
    1: 'kaum',
    2: 'wenig',
    3: 'eine gute Menge an',
    4: 'viel',
    5: 'sehr viel'
    }
    work_levels = {
    'Niedrig': 'wenig',
    'Mittel': 'mittelmäßig viel',
    'Hoch': 'sehr viel',
    }
    light_lv = light_levels.get(light, 'unbekannt')
    water_lv = water_levels.get(water, 'unbekannt')
    time_lv = work_levels.get(time, 'unbekannt')

    
    prompt = 'Ich plane ein neues Gartenbeet. Wo das Beet aufgebaut wird ist es '+light_lv+' sonnig. Das Beet ist in Richtung '+alignment+' ausgerichtet. Für die Versorgung des Beets habe ich '+water_lv+' Wasser zur Verfügung. Auf jeden Fall will ich folgende Pflanzen in meinem Beet anbauen: '+plant_names_str+'. Der Boden in meinem besteht aus viel '+soil+'. Ich habe für mein Beet '+time_lv+' Zeit. Ich bin mir nicht sicher, ob ich diese Pflanze in meinem Beet anbauen kann: '+check_plant_name+'. Bitte liefere mir ein array mit genau einem Wert zwischen 0 (passt überhaupt nicht) und 5 (passt total), welcher angibt, wie gut diese Pflanze in mein Beet passt.'

    return prompt