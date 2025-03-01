from flask import Flask, jsonify
from threading import Thread
import logging
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

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
        return jsonify({
            'status': 'healthy',
            'server': 'flask',
            'port': 5000
        })
    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        return jsonify({'status': 'error', 'message': str(e)}), 500

def run():
    """Run the Flask server"""
    try:
        logger.info("Starting Flask server on port 5000...")
        app.run(host='0.0.0.0', port=5000)
    except Exception as e:
        logger.error(f"Failed to start Flask server: {e}", exc_info=True)
        raise

def keep_alive():
    """Start the server in a separate thread"""
    try:
        logger.info("Starting keep_alive thread...")
        t = Thread(target=run, daemon=True)
        t.start()
        logger.info("Keep_alive thread started successfully")
    except Exception as e:
        logger.error(f"Failed to start keep_alive thread: {e}", exc_info=True)
        raise