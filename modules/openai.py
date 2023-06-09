import openai
#----------------- LOCAL TESTING -----------------#
# import config
# OPEN_AI_KEY = config.OPEN_AI_KEY
#-------------------------------------------------#

#----------------- DEPLOYMENT -----------------#
import os
OPEN_AI_KEY = os.environ.get('OPEN_AI_KEY')
#-------------------------------------------------#

def request_open_ai(text: str):
    openai.api_key = OPEN_AI_KEY
    response = openai.Completion.create(model="text-davinci-003", prompt=text, temperature=0.5, max_tokens=1000)

    return response["choices"][0]["text"]

def request_open_ai_image(plant: str = None, prompt: str = None, img_size: str = "256x256"):
    #make prompt and plant optinal, so the standard prompt still works to generate an img for a plant, but also allow to generate an img for the wiss database
    if prompt:
        ai_prompt = prompt
    else:
        ai_prompt = "Eine" + plant + "in einem Garten bei gutem Wetter kurz nachdem es geregnet hat wobei die Pflanze von den ersten Sonnenstrahlen getroffen wird."
    openai.api_key = OPEN_AI_KEY
    response = openai.Image.create(
    prompt=ai_prompt,
    n=1,
    size=img_size
    )
    image_url = response['data'][0]['url']
    return image_url, plant

