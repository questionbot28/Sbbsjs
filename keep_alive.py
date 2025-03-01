from flask import Flask, jsonify
from threading import Thread
import os
import logging
import time

# Configure logging
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
    logger.info("Home endpoint accessed")
    return "I'm alive!"

@app.route('/health')
def health():
    """Health check endpoint"""
    try:
        logger.info("Health check endpoint accessed")
        status = {
            'status': 'healthy',
            'uptime_seconds': int(time.time() - start_time),
            'server': 'flask',
            'port': 5000
        }
        logger.info(f"Health check successful: {status}")
        return jsonify(status)
    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        return jsonify({'status': 'error', 'message': str(e)}), 500

def run():
    """Run the Flask server"""
    try:
        # Always use port 5000 for Replit
        logger.info("Starting Flask server on port 5000...")
        app.run(
            host='0.0.0.0',  # Bind to all interfaces
            port=5000,
            debug=False
        )
    except Exception as e:
        logger.error(f"Failed to start Flask server: {e}", exc_info=True)
        raise

def keep_alive():
    """Start the server in a separate thread"""
    try:
        logger.info("Starting keep_alive thread...")
        t = Thread(target=run, daemon=True)
        t.start()
        # Give the server a moment to start
        time.sleep(2)
        logger.info("Keep_alive thread started successfully")
    except Exception as e:
        logger.error(f"Failed to start keep_alive thread: {e}", exc_info=True)
        raise