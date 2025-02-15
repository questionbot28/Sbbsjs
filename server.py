import eventlet
eventlet.monkey_patch()

import os
import logging
from flask import Flask, jsonify, render_template, send_from_directory
from flask_cors import CORS
import trafilatura
import json
import aiohttp
from bs4 import BeautifulSoup
import asyncio
import requests

# Configure logging with more detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

def fetch_youtube_trending():
    """Fetch trending music from YouTube Music"""
    try:
        url = "https://music.youtube.com/trending"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        }

        # Use synchronous requests for Flask compatibility
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            html = response.text
            soup = BeautifulSoup(html, 'html.parser')

            # Extract trending songs
            songs = []
            song_elements = soup.find_all('ytmusic-responsive-list-item-renderer')

            logger.info(f"Found {len(song_elements)} song elements")

            for element in song_elements[:10]:  # Get top 10 songs
                try:
                    title_element = element.find('yt-formatted-string', {'class': 'title'})
                    artist_element = element.find('yt-formatted-string', {'class': 'subtitle'})
                    video_id = element.get('video-id', '')

                    if title_element and artist_element:
                        song_info = {
                            'title': title_element.text.strip(),
                            'artist': artist_element.text.strip(),
                            'videoId': video_id
                        }
                        songs.append(song_info)
                        logger.info(f"Added song: {song_info}")
                except Exception as e:
                    logger.error(f"Error processing song element: {str(e)}")
                    continue

            return songs
        else:
            logger.error(f"Failed to fetch trending songs: {response.status_code}")
            # Return sample data as fallback
            return [
                {"title": "Latest Hit 1", "artist": "Artist 1", "videoId": "dQw4w9WgXcQ"},
                {"title": "Latest Hit 2", "artist": "Artist 2", "videoId": "9bZkp7q19f0"},
                {"title": "Latest Hit 3", "artist": "Artist 3", "videoId": "kJQP7kiw5Fk"}
            ]
    except Exception as e:
        logger.error(f"Error fetching trending songs: {str(e)}")
        return []

@app.route('/api/trending')
def get_trending():
    """API endpoint to get trending songs"""
    try:
        logger.info("Fetching trending songs...")
        songs = fetch_youtube_trending()
        logger.info(f"Fetched {len(songs)} trending songs")
        return jsonify(songs)
    except Exception as e:
        logger.error(f"Error in trending endpoint: {str(e)}")
        return jsonify([]), 500

@app.route('/')
def index():
    logger.info("Received request for index route")
    return render_template('index.html')

@app.route('/health')
def health():
    logger.info("Received request for health check")
    return jsonify({"status": "healthy"})

@app.route('/static/<path:filename>')
def serve_static(filename):
    logger.info(f"Serving static file: {filename}")
    return send_from_directory('static', filename)

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