#keys
from PIL import Image
from io import BytesIO
import requests


def upload_plant(id, item, collection, CLIENT):
    db = CLIENT
    #Add the new document to the "plants" collection
    doc_ref = db.collection(collection).document(str(id))
    doc_ref.set(item)
    return "success"

def upload_image(image_url, name, folder, img_size, BUCKET):
    #get the image from the url
    response = requests.get(image_url)
    #compressing the image
    img = compress_img(response,img_size)
    #upload image to firebase storage
    blob = BUCKET.blob(folder+name)
    url =blob.upload_from_string(img, content_type=response.headers['content-type'])
    url = blob.public_url
    return folder+name, url

def compress_img(response, img_size):
    #compressing the image
    img = Image.open(BytesIO(response.content))
    img.thumbnail((int(img_size),int(img_size)), Image.ANTIALIAS)

    # Create an in-memory buffer to store the compressed image
    output_buffer = BytesIO()

    img.save(output_buffer, format='JPEG', quality=80)
    return output_buffer.getvalue()