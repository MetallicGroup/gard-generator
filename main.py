from flask import Flask, request, jsonify
import requests
import base64
from io import BytesIO
from PIL import Image

app = Flask(__name__)

# === CONFIG ===
IMGBB_API_KEY = "34f2316153715d983301e6a9632fc59d"  # <-- INLOCUIESTE cu cheia ta reala de la imgbb.com

# === UTIL: Upload imagine pe ImgBB ===
def upload_to_imgbb(image: Image.Image):
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    img_base64 = base64.b64encode(buffered.getvalue()).decode()

    response = requests.post(
        "https://api.imgbb.com/1/upload",
        params={"key": IMGBB_API_KEY},
        data={"image": img_base64}
    )

    if response.status_code == 200:
        return response.json()["data"]["url"]
    else:
        return None

# === FAKE GENERATOR (inlocuieste cu AI real mai tarziu) ===
def generate_fake_image(image_url, model):
    # Descarcă imaginea originală
    response = requests.get(image_url)
    image = Image.open(BytesIO(response.content)).convert("RGB")

    # Simulare: doar adăugăm text cu modelul ales peste imagine
    from PIL import ImageDraw, ImageFont
    draw = ImageDraw.Draw(image)
    draw.text((10, 10), f"Model: {model}", fill=(255, 0, 0))

    return image

# === ENDPOINT PRINCIPAL ===
@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json()

    image_url = data.get("image_url")
    model = data.get("model")
    nume = data.get("nume")
    telefon = data.get("telefon")

    if not image_url or not model:
        return jsonify({"error": "Faltă imaginea sau modelul"}), 400

    # Generează imaginea cu modelul (de test)
    generated_image = generate_fake_image(image_url, model)

    # Încarcă pe ImgBB
    imgbb_url = upload_to_imgbb(generated_image)

    if not imgbb_url:
        return jsonify({"error": "Nu s-a putut urca imaginea"}), 500

    return jsonify({"image_link": imgbb_url})

# === VERIFICARE ===
@app.route("/")
def index():
    return "API Gard Generator activ. Folosește /generate pentru POST."

if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=5000)
