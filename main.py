from flask import Flask, request, jsonify
import requests
import base64
from PIL import Image, ImageDraw
from io import BytesIO
import os

app = Flask(__name__)

# Ia cheia din variabilele de mediu (setată în Render)
IMGBB_API_KEY = os.getenv('IMGBB_API_KEY')

# Funcție pentru upload pe ImgBB
def upload_to_imgbb(image_bytes):
    encoded_image = base64.b64encode(image_bytes).decode('utf-8')
    response = requests.post(
        'https://api.imgbb.com/1/upload',
        data={'key': IMGBB_API_KEY, 'image': encoded_image}
    )
    response.raise_for_status()
    return response.json()['data']['url']

# Endpoint principal care primește cererea de la Landbot
@app.route('/process', methods=['POST'])
def process():
    data = request.json
    image_url = data.get('image_url')
    model = data.get('model')

    try:
        # 1. Descarcă imaginea originală de la client
        response = requests.get(image_url)
        original_image = Image.open(BytesIO(response.content))

        # 2. Simulează adăugarea unui model de gard (text pe imagine)
        img_draw = original_image.copy()
        draw = ImageDraw.Draw(img_draw)
        draw.text((20, 20), f"Model gard: {model}", fill=(255, 0, 0))

        # 3. Salvează imaginea în memorie (ca bytes)
        img_byte_arr = BytesIO()
        img_draw.save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()

        # 4. Trimite imaginea pe ImgBB
        imgbb_url = upload_to_imgbb(img_byte_arr)

        # 5. Returnează linkul în JSON
        return jsonify({'image_url': imgbb_url})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Pornirea serverului în Render (PORT setat automat)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
