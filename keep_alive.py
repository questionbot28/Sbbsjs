from flask import Flask
from threading import Thread
import time

app = Flask(__name__)

@app.route('/')
def home():
    return "I'm alive!"

def run():
    try:
        app.run(host="0.0.0.0", port=8081)
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"Error: Port 8081 is already in use.  Try a different port.")
        else:
            print(f"An unexpected error occurred: {e}")


def keep_alive():
    # Add initial delay before starting the web server
    time.sleep(2)  # Wait 2 seconds before starting
    t = Thread(target=run)
    t.daemon = True  # Make thread daemon so it exits when main thread exits
    t.start()