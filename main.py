from flask import Flask, request, jsonify
import os
from openai import OpenAI

app = Flask(__name__)

# Inițializează clientul OpenAI
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# PROMPTURI pentru fiecare model
model_prompts = {
    "MX15": "Un gard rezidențial modern compus din panouri metalice gri închis, fiecare cu 7 lamele orizontale tip jaluzea, înclinate la aproximativ 35 de grade. Lamelele au grosimea de 40 mm, sunt distanțate la 30 mm între ele și sunt încadrate într-un chenar metalic gros de 50 mm. Panoul gardului are aproximativ 1500 mm lățime și 1000 mm înălțime. Panourile sunt montate între stâlpi tencuiți bej, de 300 mm lățime și 1500 mm înălțime, fixați pe un soclu de beton de 400 mm înălțime. Designul este modern-industrial, robust și simetric, ideal pentru o locuință contemporană.",
    "MX25": "Gard metalic orizontal cu lamele de grosime medie, înclinate la 25 de grade, distanțate la 25 mm între ele, cu cadru de 50 mm și culoare maro RAL 8017. Stil modern și aerisit.",
    "MX60": "Gard modern cu lamele late, orizontale, distanțate, vopsite gri antracit, cu cadru gros și aspect industrial. Ideal pentru case contemporane."
}

@app.route("/generare", methods=["POST"])
def generare():
    data = request.json
    model = data.get("model_gard")
    poza = data.get("poza_gard")

    if not model or not poza:
        return jsonify({"error": "Lipsește modelul sau poza"}), 400

    prompt = f"{model_prompts.get(model, '')} Înlocuiește gardul din poza clientului cu acest model, păstrând casa, fundalul și proporțiile neschimbate."

    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            n=1
        )
        image_url = response.data[0].url
        return jsonify({"image_url": image_url})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/")
def home():
    return "Generator AI Garduri activ! 🛠️"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
