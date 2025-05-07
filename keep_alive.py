from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def keep_alive():
    port = int(os.environ.get("PORT", 8080))  # Render przekaże PORT
    app.run(host='0.0.0.0', port=port)
