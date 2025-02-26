from flask import Flask
from threading import Thread
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/')
def home():
    logger.info("Health check endpoint accessed")
    return "I'm alive!"

def run():
    try:
        logger.info("Starting Flask server on port 5000...")
        app.run(host="0.0.0.0", port=5000)  # Always use port 5000 for Replit
    except Exception as e:
        logger.error(f"An error occurred while starting Flask server: {e}")
        raise  # Re-raise the exception for the main thread to handle

def keep_alive():
    logger.info("Initializing keep_alive thread...")
    t = Thread(target=run)
    t.daemon = True  # Make thread daemon so it exits when main thread exits
    t.start()
    logger.info("Keep_alive thread started successfully")