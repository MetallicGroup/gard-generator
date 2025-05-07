
from flask import Flask, request, jsonify
import openai
import os

app = Flask(__name__)
openai.api_key = os.environ.get("OPENAI_API_KEY")

@app.route("/generare", methods=["POST"])
def generare():
    data = request.json
    model = data.get("model_gard", "MX25")
    poza = data.get("poza_gard", "")
    prompt = f"Înlocuiește gardul din imaginea clientului cu un model modern {model}, cu lamele orizontale, în stil realist."

    try:
        response = openai.Image.create(
            prompt=prompt,
            n=1,
            size="1024x1024"
        )
        url = response["data"][0]["url"]
        return jsonify({"image_url": url})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/")
def home():
    return "Generator AI Garduri activ pe Render!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
