from flask import Flask, request
from modules import plants
from modules import weather


app = Flask(__name__, static_folder="./templates/static")


#url-routes 
@app.route('/')
def index():
    return "true"

@app.route("/ai", methods=["POST"])
def request_open_ai():
    try:
        body = request.get_json()

        if "ai_request" not in body or body["ai_request"] is None or body["ai_request"].strip() == "":
            return "error - no text given"
        ai_request = body["ai_request"].strip()

        new_text = plants.request_open_ai(ai_request)
        return new_text
    except Exception as e:
        return str(e)
    
@app.route("/get_plant")
def get_plant():
    try:
        name = request.args.get('name')
        response = plants.plantlookup(name)
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
    
if __name__ == "__main__": app.run(debug=False,  host='0.0.0.0', port=8080)
