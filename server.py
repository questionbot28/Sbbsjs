import os
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_socketio import SocketIO
from flask_cors import CORS
import threading
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('discord_bot')
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

# Initialize Flask app with proper static and template folders
static_folder = Path('static')
template_folder = Path('templates')
static_folder.mkdir(parents=True, exist_ok=True)
template_folder.mkdir(parents=True, exist_ok=True)

app = Flask(__name__, static_folder=str(static_folder), template_folder=str(template_folder))
socketio = SocketIO(app, cors_allowed_origins="*", logger=True, engineio_logger=True)
CORS(app)

# Store current song info and user preferences
now_playing = {
    "title": "No song playing",
    "artist": "",
    "progress": 0,
    "duration": 100,
    "thumbnail": "https://via.placeholder.com/150",
    "is_playing": False
}

user_preferences = {}  # Stores user settings like language
music_queue = []  # Stores the music queue

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    """Serve React application"""
    try:
        if path and (static_folder / path).exists():
            return send_from_directory(app.static_folder, path)
        return render_template("index.html")
    except Exception as e:
        logger.error(f"Error serving path {path}: {e}")
        return render_template("index.html")

@app.route('/api/alive')
def alive():
    """Keep-alive endpoint"""
    return jsonify({"status": "alive"})

@app.route("/api/queue", methods=["GET", "POST"])
def queue():
    """Handle queue operations"""
    global music_queue
    try:
        if request.method == "POST":
            song = request.json.get("song")
            if song:
                music_queue.append(song)
                socketio.emit("update_queue", music_queue)
                logger.info(f"Added song to queue: {song}")
        return jsonify({"queue": music_queue})
    except Exception as e:
        logger.error(f"Error in queue management: {e}")
        return jsonify({"error": "Failed to process queue operation"}), 500

@app.route("/api/language", methods=["POST"])
def change_language():
    """Handle language preference changes"""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400

        user = data.get("user_id")
        lang = data.get("language")

        if not all([user, lang]):
            return jsonify({"error": "Missing required fields"}), 400

        user_preferences[user] = lang
        logger.info(f"Updated language preference for user {user} to {lang}")
        return jsonify({"message": "Language updated", "language": lang})
    except Exception as e:
        logger.error(f"Error changing language: {e}")
        return jsonify({"error": str(e)}), 500

@socketio.on("connect")
def handle_connect():
    """Handle client connection"""
    try:
        logger.info("Client connected to websocket")
        socketio.emit("nowPlaying", now_playing)
        socketio.emit("update_queue", music_queue)
    except Exception as e:
        logger.error(f"Error in handle_connect: {e}")

@socketio.on("disconnect")
def handle_disconnect():
    """Handle client disconnection"""
    logger.info("Client disconnected from websocket")

@socketio.on("playPause")
def handle_play_pause(is_playing):
    """Handle play/pause requests from web UI"""
    try:
        global now_playing
        now_playing["is_playing"] = is_playing
        logger.info(f"Play/Pause state changed to: {is_playing}")
        socketio.emit("playbackStateChanged", {"is_playing": is_playing})
    except Exception as e:
        logger.error(f"Error in handle_play_pause: {e}")

@socketio.on("skipSong")
def handle_skip():
    """Handle skip song requests"""
    try:
        logger.info("Skip song requested")
        if hasattr(app, "music_bot"):
            app.music_bot.skip()
    except Exception as e:
        logger.error(f"Error in handle_skip: {e}")

@socketio.on("prevSong")
def handle_previous():
    """Handle previous song requests"""
    try:
        logger.info("Previous song requested")
        if hasattr(app, "music_bot"):
            app.music_bot.previous()
    except Exception as e:
        logger.error(f"Error in handle_previous: {e}")

@socketio.on("setVolume")
def handle_volume(volume):
    """Handle volume change requests"""
    try:
        logger.info(f"Volume change requested: {volume}")
        if hasattr(app, "music_bot"):
            app.music_bot.set_volume(volume)
    except Exception as e:
        logger.error(f"Error in handle_volume: {e}")

@socketio.on("likeSong")
def handle_like(liked):
    """Handle song like/unlike requests"""
    try:
        logger.info(f"Song {'liked' if liked else 'unliked'}")
        # Implement like functionality here
        socketio.emit("likeUpdated", {"liked": liked})
    except Exception as e:
        logger.error(f"Error in handle_like: {e}")

def update_now_playing(song_info):
    """Update current song information and notify clients"""
    try:
        global now_playing
        now_playing.update(song_info)
        socketio.emit("nowPlaying", now_playing)
    except Exception as e:
        logger.error(f"Error in update_now_playing: {e}")

def run_web():
    """Run the Flask application"""
    try:
        port = int(os.getenv('PORT', 8080))
        logger.info(f"Starting web server on port {port}")
        socketio.run(app, host="0.0.0.0", port=port, use_reloader=False)
    except Exception as e:
        logger.error(f"Error running web server: {e}")
        raise

def start_web_server():
    """Start the web server in a separate thread"""
    try:
        web_thread = threading.Thread(target=run_web)
        web_thread.daemon = True
        web_thread.start()
        logger.info("Web server thread started successfully")
        return web_thread
    except Exception as e:
        logger.error(f"Error starting web server thread: {e}")
        raise

if __name__ == "__main__":
    try:
        run_web()
    except Exception as e:
        logger.error(f"Failed to start web server: {e}")