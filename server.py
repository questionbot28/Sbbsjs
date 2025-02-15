import eventlet
eventlet.monkey_patch()

import os
import logging
from flask import Flask, jsonify, render_template, send_from_directory
from flask_cors import CORS
import json
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
    """Fetch trending music from YouTube Data API"""
    try:
        api_key = os.environ.get('YOUTUBE_API_KEY')
        if not api_key:
            logger.error("YouTube API key not found in environment variables")
            return []

        url = "https://www.googleapis.com/youtube/v3/videos"
        params = {
            'part': 'snippet,statistics',
            'chart': 'mostPopular',
            'videoCategoryId': '10',  # Music category
            'maxResults': '10',
            'key': api_key
        }

        logger.info("Fetching trending music videos from YouTube API")
        response = requests.get(url, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()
            songs = []

            for item in data.get('items', []):
                try:
                    snippet = item['snippet']
                    song_info = {
                        'title': snippet['title'],
                        'artist': snippet['channelTitle'],
                        'videoId': item['id'],
                        'thumbnail': snippet['thumbnails']['high']['url'],
                        'views': item['statistics'].get('viewCount', '0')
                    }
                    songs.append(song_info)
                    logger.info(f"Added song: {song_info['title']}")
                except KeyError as e:
                    logger.error(f"Missing key in YouTube API response: {e}")
                    continue
                except Exception as e:
                    logger.error(f"Error processing video data: {e}")
                    continue

            return songs
        else:
            logger.error(f"YouTube API request failed: {response.status_code} - {response.text}")
            # Return sample data as fallback
            return [
                {
                    "title": "Example Song 1",
                    "artist": "Artist 1",
                    "videoId": "dQw4w9WgXcQ",
                    "thumbnail": "https://i.ytimg.com/vi/dQw4w9WgXcQ/hqdefault.jpg",
                    "views": "1000000"
                },
                {
                    "title": "Example Song 2",
                    "artist": "Artist 2",
                    "videoId": "9bZkp7q19f0",
                    "thumbnail": "https://i.ytimg.com/vi/9bZkp7q19f0/hqdefault.jpg",
                    "views": "2000000"
                }
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