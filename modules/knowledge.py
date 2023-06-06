from modules import openai
from modules import weather
from modules import firebase
import random
from datetime import datetime
import json
import uuid

def generate_text_content(CLIENT, BUCKET):
    #generate text parameters
    categories = ["diy", "pflegetipps", "inspiration"]
    category = random.choice(categories)
    today = datetime.today().strftime('%d.%m.%Y')
    weather_now = weather.get_weather("Mosbach")
    temperature = weather_now["temp"]
    sky = weather_now["weather"]
    humidity = weather_now["humidity"]
    wind_speed = weather_now["wind_speed"]

    txt_id = str(uuid.uuid4())
    
    #generate text
    txt_prompt = 'Erstelle einen interessanten und lustigen Wissenstext für ein Gartenmagazin in der Kategorie ' + category + 'Der Text sollte zur Saison und zum Wetter passen beschrenke dich auch auf eine spezifische Aufgabe oder ein spezifisches Gartenprojekt. Heute ist der ' + str(today) + ' und es ist ' + sky + ' bei ' + str(temperature) + ' Grad. Die Luftfeuchtigkeit beträgt ' + str(humidity) + ' Prozent und der Wind weht mit ' + str(wind_speed) + ' km/h. Liefere das Ergebnis als Array in folgendem Format zurück: {"text": "Hier ist der Text", "headline": "Hier eine passende Überschrift"}'
    ai_response = openai.request_open_ai(txt_prompt)
    text = json.loads(ai_response.replace('\n', ''))

    #generate img
    img_prompt = "Erstelle ein natürliches Bild aus einem schönen Garten für den Text in einem Gartenmagazin. Der Text hat die Überschrift" + text["headline"]+ "."
    img_url, txt_id = openai.request_open_ai_image(plant=txt_id, prompt=img_prompt, img_size="512x512")

    #build data for firestore
    text['category'] = category
    text['date'] = today
    text['id'] = txt_id
    
    #upload
    text["firebase_path"], text["img"] = firebase.upload_image(img_url, txt_id, "knowledge/",512, BUCKET)
    #push to firebase
    firebase.upload_plant(txt_id, text, "knowledge", CLIENT)

    return text

def get_all_articles(CLIENT):
    #search for Plant in Firestore
    db = CLIENT
    
    # perform a query for all articles matching the common names
    docs = db.collection('knowledge').get()

    #if plant is in the database
    if len(docs) > 0:
        articles = [doc.to_dict() for doc in docs]
        return articles
    #if plant is nowhere in the database
    else:
        return "articles not found", 400
    
def get_single_article(id: str, CLIENT):
    #search for article in Firestore
    db = CLIENT
    article_collection = db.collection('knowledge')
    docs = article_collection.get()

    #if plant is in the database
    if len(docs) > 0:
        article_doc = article_collection.where('id', '==', id).get()[0]
        article = article_doc.to_dict()
        return article