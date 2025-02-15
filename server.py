import os
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_socketio import SocketIO
from flask_cors import CORS
import threading
import logging
from pathlib import Path
import requests

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('discord_bot')

# Initialize Flask app with proper static and template folders
static_folder = Path('static')
template_folder = Path('templates')
static_folder.mkdir(parents=True, exist_ok=True)
template_folder.mkdir(parents=True, exist_ok=True)

logger.debug(f"Static folder path: {static_folder.absolute()}")
logger.debug(f"Template folder path: {template_folder.absolute()}")

app = Flask(__name__, 
           static_folder=str(static_folder), 
           template_folder=str(template_folder))
CORS(app, resources={r"/*": {"origins": "*"}})

try:
    socketio = SocketIO(app, 
                       cors_allowed_origins="*", 
                       logger=True, 
                       engineio_logger=True,
                       async_mode='threading')
    logger.info("SocketIO initialized successfully")
except Exception as e:
    logger.error(f"Error initializing SocketIO: {e}")
    exit(1) #Exit if SocketIO fails to initialize


# Store current song info and user preferences
now_playing = {
    "title": "No song playing",
    "artist": "",
    "progress": 0,
    "duration": 100,
    "thumbnail": "https://via.placeholder.com/150",
    "is_playing": False
}

user_preferences = {}  # Stores user settings like language, theme
music_queue = []  # Stores the music queue
YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY')

@app.route('/health')
def health_check():
    """Basic health check endpoint"""
    logger.debug("Health check endpoint accessed")
    return "Server is running!", 200

@app.route('/')
def index():
    """Serve the main application page"""
    logger.debug("Serving index page")
    try:
        return render_template("index.html")
    except Exception as e:
        logger.error(f"Error serving index page: {e}")
        return f"Error: {str(e)}", 500

@app.route('/<path:path>')
def serve(path):
    """Serve static files"""
    logger.debug(f"Serving path: {path}")
    try:
        if path and (static_folder / path).exists():
            return send_from_directory(app.static_folder, path)
        return render_template("index.html")
    except Exception as e:
        logger.error(f"Error serving path {path}: {e}")
        return render_template("index.html")


@app.route('/api/trending')
def get_trending():
    """Get trending music from YouTube"""
    try:
        if not YOUTUBE_API_KEY:
            return jsonify({"error": "YouTube API key not configured"}), 500

        url = "https://www.googleapis.com/youtube/v3/videos"
        params = {
            "part": "snippet",
            "chart": "mostPopular",
            "videoCategoryId": "10",  # Music category
            "maxResults": "10",
            "key": YOUTUBE_API_KEY
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            videos = response.json().get("items", [])
            trending_songs = [{
                "title": video["snippet"]["title"],
                "thumbnail": video["snippet"]["thumbnails"]["medium"]["url"],
                "videoId": video["id"]
            } for video in videos]
            return jsonify(trending_songs)
        return jsonify({"error": "Failed to fetch trending songs"}), 500
    except Exception as e:
        logger.error(f"Error fetching trending songs: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/search')
def search_songs():
    """Search for songs on YouTube"""
    try:
        query = request.args.get('q', '')
        if not query:
            return jsonify({"error": "No search query provided"}), 400

        if not YOUTUBE_API_KEY:
            return jsonify({"error": "YouTube API key not configured"}), 500

        url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            "part": "snippet",
            "q": query,
            "type": "video",
            "videoCategoryId": "10",
            "maxResults": "10",
            "key": YOUTUBE_API_KEY
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            videos = response.json().get("items", [])
            search_results = [{
                "title": video["snippet"]["title"],
                "thumbnail": video["snippet"]["thumbnails"]["medium"]["url"],
                "videoId": video["id"]["videoId"]
            } for video in videos]
            return jsonify(search_results)
        return jsonify({"error": "Failed to search songs"}), 500
    except Exception as e:
        logger.error(f"Error searching songs: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/settings', methods=['GET', 'POST'])
def handle_settings():
    """Handle user settings"""
    try:
        if request.method == 'POST':
            settings = request.json
            user_id = settings.get('user_id', 'default')
            user_preferences[user_id] = {
                'theme': settings.get('theme', 'dark'),
                'volume': settings.get('volume', 50),
                'language': settings.get('language', 'en')
            }
            return jsonify({"message": "Settings updated successfully"})
        else:
            user_id = request.args.get('user_id', 'default')
            return jsonify(user_preferences.get(user_id, {
                'theme': 'dark',
                'volume': 50,
                'language': 'en'
            }))
    except Exception as e:
        logger.error(f"Error handling settings: {e}")
        return jsonify({"error": str(e)}), 500

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

# WebSocket event handlers
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
        port = int(os.getenv('PORT', 3000))
        logger.info(f"Starting web server on port {port}")
        socketio.run(app, 
                    host="0.0.0.0", 
                    port=port,
                    debug=True,
                    use_reloader=False,
                    log_output=True)
    except Exception as e:
        logger.error(f"Error running web server: {e}")
        raise

if __name__ == "__main__":
    try:
        run_web()
    except Exception as e:
        logger.error(f"Failed to start web server: {e}")