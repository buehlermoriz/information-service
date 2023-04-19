import openai
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore



OPEN_AI_KEY = "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"
cred = credentials.Certificate(".env/lumela-2fb04-firebase-adminsdk-p8yj1-fc6b0b43d5.json")
firebase_admin.initialize_app(cred)

def request_open_ai(text: str, model: str, temp: float, max_tokens: int):
    openai.api_key = OPEN_AI_KEY
    response = openai.Completion.create(model=model, prompt=text, temperature=temp, max_tokens=max_tokens)

    return response["choices"][0]["text"]


def push_plant_to_firebase(plant: str, height: str):
    db = firestore.client()
 # Define the data for the new plant document
    data = {
        'name': plant,
        'height': height
    }

    # Add the new document to the "plants" collection
    doc_ref = db.collection('plants').document(plant)
    doc_ref.set(data)
    return "success"