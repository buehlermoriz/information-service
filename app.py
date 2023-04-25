from flask import Flask, request
from modules import plants
from modules import weather


app = Flask(__name__, static_folder="./templates/static")


#url-routes 
@app.route('/')
def index():
    return "true"

    
@app.route("/get_plant", methods=['GET', 'POST'])
def get_plant():
    try:
        #request single plant
        if request.method == 'GET':
            name = request.args.get('name')
            if(name != None):
                response = plants.plant_lookup(name)
            else:
                response = "No plant name provided.", 400
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
        return str(e)
    
@app.route("/get_weather")
def get_weather():
    try:
        city = request.args.get('city')
        # if plant is nowhere in the database
        response = weather.get_weather(city)
        return response
    except Exception as e:
        return str(e)
    
if __name__ == "__main__": app.run()
