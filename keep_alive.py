from flask import Flask, jsonify
from threading import Thread
import os
import logging
import time

# Configure logging with more detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
start_time = time.time()

@app.route('/')
def home():
    """Basic endpoint that confirms server is running"""
    logger.info("Health check endpoint accessed")
    return "I'm alive!"

@app.route('/health')
def health():
    """Detailed health check endpoint"""
    uptime = int(time.time() - start_time)
    status = {
        'status': 'healthy',
        'uptime_seconds': uptime,
        'server': 'flask',
        'port': 5000
    }
    logger.info(f"Health check returned: {status}")
    return jsonify(status)

def run():
    """Run the Flask server with proper error handling"""
    try:
        logger.info("Starting Flask server on port 5000...")
        # Always use port 5000 for Replit
        app.run(
            host="0.0.0.0",
            port=5000,
            debug=False  # Disable debug mode in production
        )
    except Exception as e:
        logger.error(f"An error occurred while starting Flask server: {e}")
        raise  # Re-raise the exception for the main thread to handle

def keep_alive():
    """Initialize and start the keep_alive thread with proper logging"""
    try:
        logger.info("Initializing keep_alive thread...")
        t = Thread(target=run)
        t.daemon = True  # Make thread daemon so it exits when main thread exits
        t.start()
        logger.info("Keep_alive thread started successfully")
    except Exception as e:
        logger.error(f"Failed to start keep_alive thread: {e}")
        raise