import os
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
from flask_cors import CORS
import threading
import logging

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app)
logger = logging.getLogger('discord_bot')

# Store current song info and user preferences
now_playing = {
    "title": "No song playing",
    "artist": "",
    "progress": 0,
    "duration": 100,
    "thumbnail": "https://via.placeholder.com/150"
}

user_preferences = {}  # Stores user settings like language
music_queue = []  # Stores the music queue

@app.route('/')
def index():
    """Main web UI route"""
    return render_template("index.html")

@app.route('/alive')
def alive():
    """Keep-alive endpoint"""
    return "I'm alive!"

@app.route("/queue", methods=["GET", "POST"])
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

@app.route("/language", methods=["POST"])
def change_language():
    """Handle language preference changes"""
    try:
        user = request.json.get("user_id")
        lang = request.json.get("language")
        if user and lang:
            user_preferences[user] = lang
            logger.info(f"Updated language preference for user {user} to {lang}")
            return jsonify({"message": "Language updated", "language": lang})
        return jsonify({"error": "Invalid request"}), 400
    except Exception as e:
        logger.error(f"Error changing language: {e}")
        return jsonify({"error": "Failed to update language"}), 500

@socketio.on("connect")
def handle_connect():
    try:
        socketio.emit("nowPlaying", now_playing)
        socketio.emit("update_queue", music_queue)
        logger.info("Web client connected")
    except Exception as e:
        logger.error(f"Error in handle_connect: {e}")

@socketio.on("skipSong")
def skip_song():
    try:
        logger.info("Skip request from Web UI")
        if hasattr(app, "music_bot"):
            app.music_bot.handle_skip_web()
    except Exception as e:
        logger.error(f"Error in skip_song: {e}")

@socketio.on("setVolume")
def set_volume(volume):
    try:
        logger.info(f"Volume changed to {volume}")
        if hasattr(app, "music_bot"):
            app.music_bot.set_volume_web(volume)
    except Exception as e:
        logger.error(f"Error in set_volume: {e}")

def update_now_playing(song_info):
    """Update the current song information"""
    try:
        global now_playing
        now_playing.update(song_info)
        socketio.emit("nowPlaying", now_playing)
        socketio.emit("update_queue", music_queue)  # Also update queue
        logger.info(f"Updated now playing: {song_info['title']}")
    except Exception as e:
        logger.error(f"Error updating now playing: {e}")

def run_web():
    """Run the Flask application"""
    try:
        port = int(os.getenv('PORT', 8080))
        socketio.run(app, host="0.0.0.0", port=port)
    except Exception as e:
        logger.error(f"Error running web server: {e}")

def start_web_server():
    """Start the web server in a separate thread"""
    try:
        web_thread = threading.Thread(target=run_web)
        web_thread.daemon = True
        web_thread.start()
        logger.info("Web server started successfully")
    except Exception as e:
        logger.error(f"Error starting web server: {e}")

if __name__ == "__main__":
    start_web_server()