import eventlet
eventlet.monkey_patch()

import os
import logging
from flask import Flask, jsonify, render_template, send_from_directory
from flask_cors import CORS
import json
import requests
from datetime import datetime, timedelta

# Configure logging with more detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Cache for storing API responses
cache = {
    'trending': {'data': None, 'timestamp': None},
    'recommended': {'data': None, 'timestamp': None},
    'new_releases': {'data': None, 'timestamp': None},
    'indian': {'data': None, 'timestamp': None},
    'punjabi': {'data': None, 'timestamp': None},
    'hindi': {'data': None, 'timestamp': None},
    'featured': {'data': None, 'timestamp': None},
    'your_mix': {'data': None, 'timestamp': None},
    'albums': {'data': None, 'timestamp': None}, #Added for albums
    'english': {'data': None, 'timestamp': None} #Added for english
}

def is_cache_valid(cache_type):
    """Check if cache is still valid (less than 5 minutes old)"""
    if not cache[cache_type]['timestamp']:
        return False
    age = datetime.now() - cache[cache_type]['timestamp']
    return age < timedelta(minutes=5)

def fetch_youtube_videos(category, search_query=None, region_code='US'):
    """Generic function to fetch music videos from YouTube Data API"""
    try:
        api_key = os.getenv('YOUTUBE_API_KEY')
        if not api_key:
            logger.error("YouTube API key not found in environment variables")
            return []

        logger.info(f"Fetching {category} videos from YouTube API")
        base_url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            'part': 'snippet',
            'maxResults': '10',
            'key': api_key,
            'type': 'video',
            'videoCategoryId': '10',  # Music category
            'regionCode': region_code,
            'q': f"music {search_query}" if search_query else "popular music"
        }

        logger.info(f"Making API request for {category} videos with query: {params.get('q')}")
        response = requests.get(base_url, params=params)

        if response.status_code != 200:
            logger.error(f"YouTube API request failed: {response.status_code} - {response.text}")
            return []

        data = response.json()
        songs = []

        for item in data.get('items', []):
            try:
                video_id = item['id']['videoId']
                snippet = item['snippet']

                # Get video statistics
                stats_url = "https://www.googleapis.com/youtube/v3/videos"
                stats_params = {
                    'part': 'statistics',
                    'id': video_id,
                    'key': api_key
                }

                stats_response = requests.get(stats_url, params=stats_params)
                if stats_response.status_code == 200:
                    stats_data = stats_response.json()
                    statistics = stats_data.get('items', [{}])[0].get('statistics', {})
                else:
                    logger.error(f"Failed to get statistics for video {video_id}")
                    statistics = {}

                song_info = {
                    'title': snippet['title'],
                    'artist': snippet['channelTitle'],
                    'videoId': video_id,
                    'thumbnail': snippet['thumbnails']['high']['url'],
                    'views': statistics.get('viewCount', '0')
                }
                songs.append(song_info)
                logger.info(f"Added {category} song: {song_info['title']}")

            except Exception as e:
                logger.error(f"Error processing video {video_id if 'video_id' in locals() else 'unknown'}: {str(e)}")
                continue

        logger.info(f"Successfully fetched {len(songs)} songs for {category}")
        return songs

    except Exception as e:
        logger.error(f"Error in fetch_youtube_videos for {category}: {str(e)}")
        return []

def fetch_youtube_trending():
    """Fetch trending music from YouTube"""
    if is_cache_valid('trending'):
        return cache['trending']['data']

    songs = fetch_youtube_videos('trending', 'trending music')
    if songs:
        cache['trending'] = {'data': songs, 'timestamp': datetime.now()}
    return songs

def fetch_new_releases():
    """Fetch new music releases"""
    if is_cache_valid('new_releases'):
        return cache['new_releases']['data']

    songs = fetch_youtube_videos('new_releases', 'new music this week')
    if songs:
        cache['new_releases'] = {'data': songs, 'timestamp': datetime.now()}
    return songs

def fetch_featured_songs():
    """Fetch featured music"""
    if is_cache_valid('featured'):
        return cache['featured']['data']

    songs = fetch_youtube_videos('featured', 'popular music hits')
    if songs:
        cache['featured'] = {'data': songs, 'timestamp': datetime.now()}
    return songs

def fetch_your_mix():
    """Fetch personalized mix"""
    if is_cache_valid('your_mix'):
        return cache['your_mix']['data']

    songs = fetch_youtube_videos('your_mix', 'music mix variety')
    if songs:
        cache['your_mix'] = {'data': songs, 'timestamp': datetime.now()}
    return songs

@app.route('/api/trending')
def get_trending():
    """API endpoint to get trending songs"""
    try:
        logger.info("Fetching trending songs...")
        songs = fetch_youtube_trending()
        return jsonify(songs)
    except Exception as e:
        logger.error(f"Error in trending endpoint: {str(e)}")
        return jsonify([]), 500

@app.route('/api/new-releases')
def get_new_releases():
    """API endpoint to get new releases"""
    try:
        logger.info("Fetching new releases...")
        songs = fetch_new_releases()
        return jsonify(songs)
    except Exception as e:
        logger.error(f"Error in new releases endpoint: {str(e)}")
        return jsonify([]), 500

@app.route('/api/featured')
def get_featured():
    """API endpoint to get featured songs"""
    try:
        logger.info("Fetching featured songs...")
        songs = fetch_featured_songs()
        return jsonify(songs)
    except Exception as e:
        logger.error(f"Error in featured endpoint: {str(e)}")
        return jsonify([]), 500

@app.route('/api/your-mix')
def get_your_mix():
    """API endpoint to get personalized mix"""
    try:
        logger.info("Fetching your mix...")
        songs = fetch_your_mix()
        return jsonify(songs)
    except Exception as e:
        logger.error(f"Error in your mix endpoint: {str(e)}")
        return jsonify([]), 500

@app.route('/api/hindi')
def get_hindi_songs():
    """API endpoint to get Hindi songs"""
    try:
        if is_cache_valid('hindi'):
            return jsonify(cache['hindi']['data'])

        songs = fetch_youtube_videos('hindi', 'new hindi songs', region_code='IN')
        if songs:
            cache['hindi'] = {'data': songs, 'timestamp': datetime.now()}
        return jsonify(songs)
    except Exception as e:
        logger.error(f"Error in hindi songs endpoint: {str(e)}")
        return jsonify([]), 500

@app.route('/api/punjabi')
def get_punjabi_songs():
    """API endpoint to get Punjabi songs"""
    try:
        if is_cache_valid('punjabi'):
            return jsonify(cache['punjabi']['data'])

        songs = fetch_youtube_videos('punjabi', 'new punjabi songs', region_code='IN')
        if songs:
            cache['punjabi'] = {'data': songs, 'timestamp': datetime.now()}
        return jsonify(songs)
    except Exception as e:
        logger.error(f"Error in punjabi songs endpoint: {str(e)}")
        return jsonify([]), 500

@app.route('/api/english')
def get_english_songs():
    """API endpoint to get English songs"""
    try:
        if is_cache_valid('english'):
            return jsonify(cache['english']['data'])

        songs = fetch_youtube_videos('english', 'new english songs', region_code='US')
        if songs:
            cache['english'] = {'data': songs, 'timestamp': datetime.now()}
        return jsonify(songs)
    except Exception as e:
        logger.error(f"Error in english songs endpoint: {str(e)}")
        return jsonify([]), 500

@app.route('/api/albums')
def get_albums():
    """API endpoint to get albums"""
    try:
        if is_cache_valid('albums'):
            return jsonify(cache['albums']['data'])

        songs = fetch_youtube_videos('albums', 'new album releases', region_code='US')
        if songs:
            cache['albums'] = {'data': songs, 'timestamp': datetime.now()}
        return jsonify(songs)
    except Exception as e:
        logger.error(f"Error in albums endpoint: {str(e)}")
        return jsonify([]), 500

@app.route('/')
def index():
    """Serve the main application page"""
    return render_template('index.html')

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    return send_from_directory('static', filename)

if __name__ == '__main__':
    try:
        port = int(os.environ.get('PORT', 8080))
        logger.info(f"Starting server on port {port}")

        app.run(
            host='0.0.0.0',
            port=port,
            debug=True
        )
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}")
        raise