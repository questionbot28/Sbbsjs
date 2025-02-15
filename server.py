import os
import logging
from flask import Flask, jsonify
from flask_cors import CORS

# Configure logging with more detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/')
def index():
    logger.info("Received request for index route")
    return jsonify({"message": "Server is running!"})

@app.route('/health')
def health():
    logger.info("Received request for health check")
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    try:
        port = int(os.environ.get('PORT', 8080))
        logger.info(f"Attempting to start server on port {port}")
        logger.info(f"Debug mode: {app.debug}")

        app.run(
            host='0.0.0.0',
            port=port,
            debug=True
        )
    except Exception as e:
        logger.error(f"Failed to start server: {e}", exc_info=True)
        raise