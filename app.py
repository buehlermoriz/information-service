from flask import Flask, request, jsonify
from modules import plants
from modules import weather
from modules import bed
import os


app = Flask(__name__, static_folder="./templates/static")


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
                response = plants.plant_lookup(name)
            else:
                response = plants.all_plants()
        #request multiple plants
        elif request.method == 'POST':
            data = request.get_json()
            name_list = data.get("names")
            if name_list:
                response = plants.plant_list_lookup(name_list)
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
            response = plants.generate_new_plant(name, id)
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
            bedId = data.get("bedId")
            light = data.get("light")
            water = data.get("water")
            soil = data.get("soil")
            time = data.get("time")
            alignment = data.get("alignment")

            #get plant Names
            plantIds = data.get("plantIds")
            plant_names = plants.plant_list_lookup(plantIds)
            common_names = []
            for plant in plant_names:
                common_names.append(plant['common_name'])
            plant_names_str = ", ".join(common_names)


            #create plantbed
            companion_plant_names = bed.find_companion_plants(light, water, plant_names_str, soil, time, alignment)
            companion_plant_ids = []
            for plant_name in companion_plant_names:
                plant = plants.plant_lookup(plant_name)
                companion_plant_ids.append(plant['id'])
            
            return response, 200
        else:
            response = "No plantbed provided.", 400
        return response
    except Exception as e:
        return str(e), 400
    
if __name__ == "__main__": app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
