from flask import Flask, request, jsonify
import requests
import base64
from PIL import Image, ImageDraw
from io import BytesIO
import os

app = Flask(__name__)

IMGBB_API_KEY = os.getenv('IMGBB_API_KEY')

def upload_to_imgbb(image_bytes):
    encoded_image = base64.b64encode(image_bytes).decode('utf-8')
    response = requests.post(
        'https://api.imgbb.com/1/upload',
        data={'key': IMGBB_API_KEY, 'image': encoded_image}
    )
    response.raise_for_status()
    return response.json()['data']['url']

@app.route('/process', methods=['POST'])
def process():
    data = request.json
    image_url = data.get('image_url')
    model = data.get('model')

    try:
        # 1. Descarcă imaginea
        response = requests.get(image_url)
        original_image = Image.open(BytesIO(response.content))

        # 2. Simulare modificare: adaugă modelul pe imagine
        img_draw = original_image.copy()
        draw = ImageDraw.Draw(img_draw)
        draw.text((20, 20), f"Model gard: {model}", fill=(255, 0, 0))

        # 3. Salvează imaginea în memorie
        img_byte_arr = BytesIO()
        img_draw.save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()

        # 4. Upload pe ImgBB
        imgbb_url = upload_to_imgbb(img_byte_arr)

        return jsonify({'image_url': imgbb_url})

    except Exception as e:
        return jsonify({'error': str(e)}), 500
