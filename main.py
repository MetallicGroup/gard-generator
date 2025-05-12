from flask import Flask, request, jsonify
import requests
import base64
import replicate
from io import BytesIO
from PIL import Image
import os

app = Flask(__name__)

# === CONFIG ===
client = replicate.Client(api_token=os.environ["REPLICATE_API_TOKEN"])

# === UTIL: descarcă imagine din URL ===
def load_image_from_url(url):
    response = requests.get(url)
    return Image.open(BytesIO(response.content)).convert("RGB")

# === CONVERT TO BASE64 ===
def image_to_base64(img: Image.Image):
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

# === PROMPT ===
def build_prompt(model_name):
    return f"""Un gard rezidențial modern compus din panouri metalice gri închis, fiecare cu 7 lamele orizontale tip jaluzea, înclinate la aproximativ 35 de grade. Lamelele au grosimea de 40 mm, sunt distanțate la 30 mm între ele și sunt încadrate într-un chenar metalic gros de 50 mm. Panoul gardului are aproximativ 1500 mm lățime și 1000 mm înălțime. Panourile sunt montate între stâlpi tencuiți bej, de 300 mm lățime și 1500 mm înălțime, fixați pe un soclu de beton de 400 mm înălțime. Designul este modern-industrial, robust și simetric, ideal pentru o locuință contemporană. Modelul solicitat: {model_name}. Iluminarea este naturală, de zi, punând în evidență textura metalului și umbrele formate între lamele."""

# === CALL SAM MODEL (Replicate) ===
def get_mask_from_replicate(image: Image.Image):
    output = client.run(
        "nateraw/sam",
        input={
            "image": image_to_base64(image),
        }
    )
    mask_url = output[0] if isinstance(output, list) else output.get("mask")
    mask_img = load_image_from_url(mask_url)
    return mask_img

# === CALL SD-INPAINTING MODEL (Replicate) ===
def inpaint_with_replicate(image: Image.Image, mask: Image.Image, prompt: str):
    image = image.resize((512, 512))
    mask = mask.resize((512, 512))

    output = client.run(
        "stability-ai/stable-diffusion-inpainting:fb7c6c34c7b83d7ff6826d8c3d60c7866e71860b167e16fba1c0a61c911b03ec",
        input={
            "image": image_to_base64(image),
            "mask": image_to_base64(mask),
            "prompt": prompt,
            "num_outputs": 1,
            "guidance_scale": 7.5,
            "num_inference_steps": 50
        }
    )
    return output[0] if isinstance(output, list) else output

# === ENDPOINT ===
@app.route("/generate", methods=["POST"])
def generate():
    try:
        data = request.get_json(force=True)
        print("▶️ JSON primit:", data, flush=True)

        if not data:
            return jsonify({"error": "Body JSON invalid sau gol"}), 400

        image_url = data.get("image_url")
        model = data.get("model")

        if not image_url or not model:
            return jsonify({"error": "Lipsesc parametrii obligatorii"}), 400

        print("▶️ Primit URL:", image_url, "Model:", model, flush=True)

        original = load_image_from_url(image_url)
        print("✅ Imagine originală descărcată", flush=True)

        mask = get_mask_from_replicate(original)
        print("✅ Mască generată", flush=True)

        prompt = build_prompt(model)
        print("🧠 Prompt generat:", prompt[:60], flush=True)

        result_url = inpaint_with_replicate(original, mask, prompt)
        print("✅ Imagine AI generată:", result_url, flush=True)

        return jsonify({"image_link": result_url})

    except Exception as e:
        print("🔥 EROARE:", str(e), flush=True)
        return jsonify({"error": str(e)}), 500

@app.route("/")
def index():
    return "✅ Gard Generator activ - folosește /generate"

if __name__ == "__main__":
    from waitress import serve
    import os
    port = int(os.environ.get("PORT", 5000))
    serve(app, host="0.0.0.0", port=port)
