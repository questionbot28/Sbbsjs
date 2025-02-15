from flask import Flask
from threading import Thread
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "I'm alive!"

def run():
    try:
        # Use Glitch's dynamic port or fallback to 8080
        port = int(os.getenv('PORT', 8080))
        app.run(host="0.0.0.0", port=port)
    except Exception as e:
        print(f"An error occurred: {e}")

def keep_alive():
    t = Thread(target=run)
    t.daemon = True  # Make thread daemon so it exits when main thread exits
    t.start()