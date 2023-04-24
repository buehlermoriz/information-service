from flask import Flask


app = Flask(__name__, static_folder="./templates/static")


#url-routes 
@app.route('/')
def index():
    return "true"
    
if __name__ == "__main__": app.run()
