from flask import Flask, jsonify, request
from threading import Thread
import logging
import time
import socket

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
    logger.info(f"Home endpoint accessed from {request.remote_addr}")
    return jsonify({"status": "alive", "timestamp": time.time()})

@app.route('/health')
def health():
    """Health check endpoint"""
    try:
        logger.info(f"Health check accessed from {request.remote_addr}")
        status = {
            'status': 'healthy',
            'server': 'flask',
            'port': 5000,
            'timestamp': time.time()
        }
        logger.info(f"Health check responding with: {status}")
        return jsonify(status)
    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        return jsonify({'status': 'error', 'message': str(e)}), 500

def is_port_available(port):
    """Check if the port is available"""
    try:
        # Try to bind to the port
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('0.0.0.0', port))
            s.close()
            return True
    except:
        return False

def run():
    """Run the Flask server"""
    try:
        # Check if port is available
        if not is_port_available(5000):
            logger.error("Port 5000 is already in use!")
            raise Exception("Port 5000 is already in use")

        logger.info("Starting Flask server on port 5000...")
        # Debug mode disabled, but detailed logging enabled
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=False,
            use_reloader=False
        )
    except Exception as e:
        logger.error(f"Failed to start Flask server: {e}", exc_info=True)
        raise

def keep_alive():
    """Start the server in a separate thread"""
    try:
        logger.info("Starting keep_alive thread...")
        server_thread = Thread(target=run, daemon=True)
        server_thread.start()
        logger.info("Server thread started, giving it time to initialize...")

        # Wait for port to become unavailable (indicating server has started)
        start_time = time.time()
        while is_port_available(5000):
            if time.time() - start_time > 5:  # 5 second timeout
                raise Exception("Server failed to start within timeout period")
            time.sleep(0.1)

        logger.info("Keep_alive thread setup completed")
    except Exception as e:
        logger.error(f"Failed to start keep_alive thread: {e}", exc_info=True)
        raise