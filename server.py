import os
from flask import Flask, render_template
from flask_socketio import SocketIO
import threading
import logging

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
logger = logging.getLogger('discord_bot')

# Store current song info
now_playing = {
    "title": "No song playing",
    "artist": "",
    "progress": 0,
    "duration": 100,
    "thumbnail": "https://via.placeholder.com/150"
}

@app.route('/')
def index():
    """Main web UI route"""
    return render_template("index.html")

@app.route('/alive')
def alive():
    """Keep-alive endpoint"""
    return "I'm alive!"

@socketio.on("connect")
def handle_connect():
    try:
        socketio.emit("nowPlaying", now_playing)
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