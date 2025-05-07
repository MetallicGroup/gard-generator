from flask import Flask, request, jsonify
import openai
import os

app = Flask(__name__)
openai.api_key = os.environ.get("OPENAI_API_KEY")

@app.route("/generare", methods=["POST"])
def generare():
    data = request.json
    model = data.get("model_gard", "MX25")
    prompt = f"Un gard modern model {model}, cu lamele orizontale, montat în fața unei case, în stil realist."

    try:
        response = openai.images.generate(
            model="dall-e-3",
            prompt=prompt,
            n=1,
            size="1024x1024",
            quality="standard"
        )
        image_url = response.data[0].url
        return jsonify({"image_url": image_url})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/")
def home():
    return "Generator AI Garduri activ!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
