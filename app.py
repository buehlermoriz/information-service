from flask import Flask, request, jsonify
from modules import plants
from modules import weather
from modules import bed
from modules import knowledge
import os

#keys
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from google.cloud import storage
from google.oauth2 import service_account

#----------------- LOCAL TESTING -----------------#
# cred = credentials.Certificate(".venv/keys.json")
# storage_client = storage.Client.from_service_account_json(".venv/keys.json")
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

app = Flask(__name__, static_folder="./templates/static")

firebase_admin.initialize_app(cred)
BUCKET = storage_client.get_bucket('lumela-2fb04.appspot.com')
CLIENT = firestore.client()


#url-routes 
@app.route('/')
def index():
    return jsonify({"online": True}), 200

    
@app.route("/get_plant", methods=['GET', 'POST'])
def get_plant():
    try:
        #request single plant
        if request.method == 'GET':
            name = request.args.get('name')
            if(name != None):
                response = plants.plant_lookup(name,CLIENT, BUCKET)
            else:
                response = plants.all_plants(CLIENT)
        #request multiple plants
        elif request.method == 'POST':
            data = request.get_json()
            name_list = data.get("names")
            if name_list:
                response = plants.plant_list_lookup(name_list,CLIENT)
            else:
                response = "No plant names provided.", 400
        return response
    except Exception as e:
        return str(e), 400
    
@app.route("/get_weather")
def get_weather():
    try:
        city = request.args.get('city')
        response = weather.get_weather(city)
        return response
    except Exception as e:
        return str(e), 400
    
@app.route("/reload_plant")
def reload_plant():
    try:
        name = request.args.get('name')
        id = request.args.get('id')
        if(name != None):
            response = plants.generate_new_plant(name, CLIENT, BUCKET, id)
        else:
            response = "No plant name provided.", 400
        return response
    except Exception as e:
        return str(e)
      
@app.route("/compleete_bed", methods=['POST'])
def compleete_bed():
    try:
        data = request.get_json()
        if data:
            #gather data
            light = data.get("light")
            water = data.get("water")
            soil = data.get("soil")
            time = data.get("time")
            alignment = data.get("alignment")

            #get plant Names
            plantIds = data.get("plantIds")
            plant_names = plants.plant_list_lookup(plantIds, CLIENT)
            common_names = []
            for plant in plant_names:
                common_names.append(plant['common_name'])
            plant_names_str = ", ".join(common_names)


            #create plantbed
            companion_plant_names = bed.find_companion_plants(light, water, plant_names_str, soil, time, alignment)
            companion_plant_ids = []
            for plant_name in companion_plant_names:
                plant = plants.plant_lookup(plant_name, CLIENT, BUCKET)
                companion_plant_ids.append(plant['id'])
            return_value = companion_plant_ids
            return return_value, 200
        else:
            response = "No plantbed provided.", 400
        return response
    except Exception as e:
        return str(e), 400
    
#check if plant fits in bed
@app.route("/check_compatibility", methods=['POST'])
def check_compatibility():
    try:
        name = request.args.get('name')
        data = request.get_json()
        if data:
            #gather data
            light = data.get("light")
            water = data.get("water")
            soil = data.get("soil")
            time = data.get("time")
            alignment = data.get("alignment")

            #get plant Names
            plantIds = data.get("plantIds")
            plant_names = plants.plant_list_lookup(plantIds, CLIENT)
            common_names = []
            for plant in plant_names:
                common_names.append(plant['common_name'])
            plant_names_str = ", ".join(common_names)
            plant_fits_bed = bed.check_plant_compatibility(light, water, soil, time, alignment, plant_names_str, name)
            if plant_fits_bed[0] < 3:
                return_value = str(plant_fits_bed[0])
            else:
                plant = plants.plant_lookup(name, CLIENT, BUCKET)
                return_value = plant['id']


            return return_value, 200
        else:
            response = "No plantbed provided.", 400
        return response
    except Exception as e:
        return str(e), 400

# ----------------- Wiss ----------------- #
#create
@app.route("/generate_wiss_content")
def generate_wiss_content():
    try:
        response = knowledge.generate_text_content(CLIENT, BUCKET)
        return response
    except Exception as e:
        return str(e)
#read
@app.route("/get_article")
def get_article():
    try:
        id = request.args.get('id')
        if id != None:
            response = knowledge.get_single_article(id,CLIENT)
        else:
            response = knowledge.get_all_articles(CLIENT)
        return response
    except Exception as e:
        return str(e)

if __name__ == "__main__": app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))