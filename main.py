from flask import Flask, request, jsonify
import requests
import base64
import replicate
import numpy as np
import cv2
from io import BytesIO
from PIL import Image, ImageDraw
from segment_anything import sam_model_registry, SamPredictor
import os
import torch

app = Flask(__name__)

# === CONFIG ===
IMGBB_API_KEY = "34f2316153715d983301e6a9632fc59dY"  # <-- înlocuiește cu cheia ta reală
REPLICATE_API_TOKEN = "r8_cf4gl9HvWXjEITY4PoPkCGnwomSy9g32GYhoP"
os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_TOKEN

# === LOAD SAM FORȚAT PE CPU ===
SAM_CHECKPOINT = "sam_vit_h_4b8939.pth"
if not os.path.exists(SAM_CHECKPOINT):
    os.system(f"wget -q https://dl.fbaipublicfiles.com/segment_anything/{SAM_CHECKPOINT}")

sam = sam_model_registry["vit_h"](checkpoint=SAM_CHECKPOINT).to(torch.device("cpu"))
predictor = SamPredictor(sam)

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
    return None

# === AI GENERATOR ===
def generate_image_with_replicate(input_image, mask_image, prompt):
    input_image = input_image.resize((512, 512))
    mask_image = mask_image.resize((512, 512))

    buffer_input = BytesIO()
    buffer_mask = BytesIO()
    input_image.save(buffer_input, format="PNG")
    mask_image.save(buffer_mask, format="PNG")

    output_url = replicate.run(
        "stability-ai/stable-diffusion-inpainting:fb7c6c34c7b83d7ff6826d8c3d60c7866e71860b167e16fba1c0a61c911b03ec",
        input={
            "image": base64.b64encode(buffer_input.getvalue()).decode(),
            "mask": base64.b64encode(buffer_mask.getvalue()).decode(),
            "prompt": prompt,
            "num_outputs": 1,
            "guidance_scale": 7.5,
            "num_inference_steps": 50
        }
    )
    return output_url[0] if output_url else None

# === MASCĂ CU SAM ===
def generate_mask(image: Image.Image):
    image_np = np.array(image.convert("RGB"))
    predictor.set_image(image_np)
    h, w = image_np.shape[:2]
    input_point = np.array([[w//2, h-100]])
    input_label = np.array([1])

    masks, scores, logits = predictor.predict(
        point_coords=input_point,
        point_labels=input_label,
        multimask_output=True,
    )
    mask = masks[0]
    return Image.fromarray((mask * 255).astype(np.uint8))

# === PROMPTUL TĂU ===
def build_prompt(model_name):
    return f"""Un gard rezidențial modern compus din panouri metalice gri închis, fiecare cu 7 lamele orizontale tip jaluzea, înclinate la aproximativ 35 de grade. Lamelele au grosimea de 40 mm, sunt distanțate la 30 mm între ele și sunt încadrate într-un chenar metalic gros de 50 mm. Panoul gardului are aproximativ 1500 mm lățime și 1000 mm înălțime. Panourile sunt montate între stâlpi tencuiți bej, de 300 mm lățime și 1500 mm înălțime, fixați pe un soclu de beton de 400 mm înălțime. Designul este modern-industrial, robust și simetric, ideal pentru o locuință contemporană. Modelul solicitat: {model_name}. Iluminarea este naturală, de zi, punând în evidență textura metalului și umbrele formate între lamele."""

# === ENDPOINT ===
@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json()
    image_url = data.get("image_url")
    model = data.get("model")

    if not image_url or not model:
        return jsonify({"error": "Imaginea și modelul sunt obligatorii"}), 400

    try:
        response = requests.get(image_url)
        input_image = Image.open(BytesIO(response.content)).convert("RGB")
        mask_image = generate_mask(input_image)

        prompt = build_prompt(model)
        result_url = generate_image_with_replicate(input_image, mask_image, prompt)

        if result_url:
            return jsonify({"image_link": result_url})
        else:
            return jsonify({"error": "Eroare la generarea imaginii"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/")
def index():
    return "API Gard Generator activ – POST /generate"

if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=5000)
    
