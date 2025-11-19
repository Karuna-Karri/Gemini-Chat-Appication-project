from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
MODEL_NAME = os.getenv('MODEL_NAME')  # e.g. "models/text-bison-001"

if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not set in environment variables.")

# safety check: don't treat API keys as model names
if MODEL_NAME and MODEL_NAME.startswith("AIza"):
    raise SystemExit("MODEL_NAME looks like an API key. Put the key in GOOGLE_API_KEY and set MODEL_NAME to a model id (or leave it empty to list models).")

genai.configure(api_key=GOOGLE_API_KEY)

# if no model set, list available models and exit so you can pick one
if not MODEL_NAME:
    try:
        print("MODEL_NAME not set. Listing available models (pick one and set MODEL_NAME in .env):")
        models = genai.list_models()
        for m in models:
            # print whatever representation is available
            print(getattr(m, "name", None) or getattr(m, "model", None) or m)
    except Exception as e:
        print("Failed to list models:", e)
    raise SystemExit("Set MODEL_NAME in .env to a supported model id and re-run.")

# create model/chat with chosen model id
model = genai.GenerativeModel(MODEL_NAME)
chat = model.start_chat(history=[])

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat_response():
    user_input = request.json.get('message')
    if not user_input:
        return jsonify({"error": "No message provided"}), 400
    try:
        response = chat.send_message(user_input).text
        return jsonify({"response": response})
    except Exception as e:
        print(f"ERROR:{e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)