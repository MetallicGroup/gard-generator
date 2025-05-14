# main.py (FastAPI backend pentru Render)

import os
import requests
from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import JSONResponse
from tempfile import NamedTemporaryFile
import replicate

app = FastAPI()

# === Config ===
REPLICATE_TOKEN = os.getenv("REPLICATE_API_TOKEN")
IMGBB_API_KEY = os.getenv("IMGBB_API_KEY")

# === Utilitare ===
def save_temp_file(upload_file):
    with NamedTemporaryFile(delete=False, suffix=".png") as tmp:
        tmp.write(upload_file.file.read())
        return tmp.name

# === Endpoint principal ===
@app.post("/generate")
async def generate_image(
    image: UploadFile,
    model: str = Form(...)
):
    if not REPLICATE_TOKEN or not IMGBB_API_KEY:
        return JSONResponse(status_code=500, content={"error": "Missing Replicate or ImgBB keys."})

    replicate.Client(api_token=REPLICATE_TOKEN)

    # 1. Salvare imagine temporară
    input_path = save_temp_file(image)

    # 2. Segmentare SAM (gardul)
    sam_output = replicate.run(
        "bytefury/autonomous-sam",
        input={"image": open(input_path, "rb"), "automatic": True}
    )
    mask_url = sam_output[0] if isinstance(sam_output, list) else sam_output

    # 3. Inpainting cu Stable Diffusion
    inpaint_result = replicate.run(
        "cjwbw/stable-diffusion-inpainting",
        input={
            "image": open(input_path, "rb"),
            "mask": mask_url,
            "prompt": f"black metal fence, model {model}, replacing old fence, modern house in background, same perspective, realistic lighting"
        }
    )

    final_image_url = inpaint_result

    # 4. Upload pe ImgBB
    image_data = requests.get(final_image_url).content
    imgbb_response = requests.post(
        "https://api.imgbb.com/1/upload",
        params={"key": IMGBB_API_KEY},
        files={"image": image_data}
    )
    imgbb_url = imgbb_response.json()["data"]["url"]

    return {"image_url": imgbb_url}
