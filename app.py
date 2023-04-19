from flask import Flask, request
from modules import connectors


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

        model = "text-davinci-003" if "model" not in body else body["model"]
        temp = 0.5 if "temperature" not in body else float(body["temperature"])
        max_tokens = 1000 if "max_tokens" not in body else body["max_tokens"]

        new_text = connectors.request_open_ai(ai_request, model, temp, max_tokens)
        return new_text
    except Exception as e:
        return str(e)

@app.route("/push_to_firebase", methods=["POST"])
def push_to_firebase():
    try:
        body = request.get_json()

        response = connectors.push_plant_to_firebase("tulip", "10")
        return response
    except Exception as e:
        return str(e)
    
@app.route("/get_plant")
def get_plant():
    try:
        name = request.args.get('name')



        # if plant is nowhere in the database
        response = connectors.plantlookup(name)
        return response
    except Exception as e:
        return str(e)
    
if __name__ == "__main__": app.run(debug=False,  host='0.0.0.0', port=8080)
