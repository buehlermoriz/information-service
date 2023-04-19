from flask import Flask
app = Flask(__name__, static_folder="./templates/static")

#url-routes
@app.route('/')
def index():
    return "true"

if __name__ == "__main__": app.run(debug=False,  host='0.0.0.0', port=8080)
