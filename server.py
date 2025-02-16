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
    'hindi': {'data': None, 'timestamp': None}
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
        api_key = os.environ.get('YOUTUBE_API_KEY')
        if not api_key:
            logger.error("YouTube API key not found in environment variables")
            return []

        url = "https://www.googleapis.com/youtube/v3/search" if search_query else "https://www.googleapis.com/youtube/v3/videos"

        params = {
            'part': 'snippet,statistics' if not search_query else 'snippet',
            'maxResults': '10',
            'key': api_key,
            'type': 'video',
            'videoCategoryId': '10',  # Music category
            'regionCode': region_code
        }

        if search_query:
            params['q'] = search_query
        else:
            params['chart'] = 'mostPopular'

        logger.info(f"Fetching {category} videos from YouTube API")
        response = requests.get(url, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()
            songs = []

            items = data.get('items', [])
            if search_query:
                # For search results, we need to fetch video statistics separately
                video_ids = [item['id']['videoId'] for item in items]
                stats_response = requests.get(
                    "https://www.googleapis.com/youtube/v3/videos",
                    params={
                        'part': 'statistics',
                        'id': ','.join(video_ids),
                        'key': api_key
                    }
                )
                stats_data = stats_response.json() if stats_response.status_code == 200 else {'items': []}
                stats_map = {item['id']: item['statistics'] for item in stats_data.get('items', [])}

            for item in items:
                try:
                    if search_query:
                        video_id = item['id']['videoId']
                        snippet = item['snippet']
                        statistics = stats_map.get(video_id, {})
                    else:
                        video_id = item['id']
                        snippet = item['snippet']
                        statistics = item.get('statistics', {})

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
                    logger.error(f"Error processing video data: {e}")
                    continue

            return songs
        else:
            logger.error(f"YouTube API request failed: {response.status_code} - {response.text}")
            return []

    except Exception as e:
        logger.error(f"Error fetching {category} songs: {str(e)}")
        return []

def fetch_youtube_trending():
    """Fetch trending music from YouTube Data API"""
    if is_cache_valid('trending'):
        return cache['trending']['data']

    songs = fetch_youtube_videos('trending')
    cache['trending'] = {'data': songs, 'timestamp': datetime.now()}
    return songs

def fetch_new_releases():
    """Fetch new music releases"""
    if is_cache_valid('new_releases'):
        return cache['new_releases']['data']

    songs = fetch_youtube_videos('new_releases', 'new music this week')
    cache['new_releases'] = {'data': songs, 'timestamp': datetime.now()}
    return songs

def fetch_indian_songs():
    """Fetch Indian music"""
    if is_cache_valid('indian'):
        return cache['indian']['data']

    songs = fetch_youtube_videos('indian', 'latest indian songs', 'IN')
    cache['indian'] = {'data': songs, 'timestamp': datetime.now()}
    return songs

def fetch_punjabi_songs():
    """Fetch Punjabi music"""
    if is_cache_valid('punjabi'):
        return cache['punjabi']['data']

    songs = fetch_youtube_videos('punjabi', 'new punjabi songs 2025')
    cache['punjabi'] = {'data': songs, 'timestamp': datetime.now()}
    return songs

def fetch_hindi_songs():
    """Fetch Hindi music"""
    if is_cache_valid('hindi'):
        return cache['hindi']['data']

    songs = fetch_youtube_videos('hindi', 'latest hindi songs')
    cache['hindi'] = {'data': songs, 'timestamp': datetime.now()}
    return songs

def fetch_featured_songs():
    """Fetch featured music from YouTube Data API"""
    if is_cache_valid('featured'):
        return cache['featured']['data']

    songs = fetch_youtube_videos('featured', 'trending music hits 2025')
    cache['featured'] = {'data': songs, 'timestamp': datetime.now()}
    return songs

def fetch_your_mix():
    """Fetch personalized mix of songs"""
    if is_cache_valid('your_mix'):
        return cache['your_mix']['data']

    # For demonstration, fetching a mix of different genres
    songs = fetch_youtube_videos('your_mix', 'popular music mix 2025')
    cache['your_mix'] = {'data': songs, 'timestamp': datetime.now()}
    return songs

# Update cache dictionary to include new categories
cache.update({
    'featured': {'data': None, 'timestamp': None},
    'your_mix': {'data': None, 'timestamp': None}
})


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

@app.route('/api/new-releases')
def get_new_releases():
    """API endpoint to get new releases"""
    try:
        logger.info("Fetching new releases...")
        songs = fetch_new_releases()
        logger.info(f"Fetched {len(songs)} new releases")
        return jsonify(songs)
    except Exception as e:
        logger.error(f"Error in new releases endpoint: {str(e)}")
        return jsonify([]), 500

@app.route('/api/indian')
def get_indian_songs():
    """API endpoint to get Indian songs"""
    try:
        logger.info("Fetching Indian songs...")
        songs = fetch_indian_songs()
        logger.info(f"Fetched {len(songs)} Indian songs")
        return jsonify(songs)
    except Exception as e:
        logger.error(f"Error in Indian songs endpoint: {str(e)}")
        return jsonify([]), 500

@app.route('/api/punjabi')
def get_punjabi_songs():
    """API endpoint to get Punjabi songs"""
    try:
        logger.info("Fetching Punjabi songs...")
        songs = fetch_punjabi_songs()
        logger.info(f"Fetched {len(songs)} Punjabi songs")
        return jsonify(songs)
    except Exception as e:
        logger.error(f"Error in Punjabi songs endpoint: {str(e)}")
        return jsonify([]), 500

@app.route('/api/hindi')
def get_hindi_songs():
    """API endpoint to get Hindi songs"""
    try:
        logger.info("Fetching Hindi songs...")
        songs = fetch_hindi_songs()
        logger.info(f"Fetched {len(songs)} Hindi songs")
        return jsonify(songs)
    except Exception as e:
        logger.error(f"Error in Hindi songs endpoint: {str(e)}")
        return jsonify([]), 500

@app.route('/api/featured')
def get_featured():
    """API endpoint to get featured songs"""
    try:
        logger.info("Fetching featured songs...")
        songs = fetch_featured_songs()
        logger.info(f"Fetched {len(songs)} featured songs")
        return jsonify(songs)
    except Exception as e:
        logger.error(f"Error in featured songs endpoint: {str(e)}")
        return jsonify([]), 500

@app.route('/api/your-mix')
def get_your_mix():
    """API endpoint to get personalized mix"""
    try:
        logger.info("Fetching your mix...")
        songs = fetch_your_mix()
        logger.info(f"Fetched {len(songs)} songs for your mix")
        return jsonify(songs)
    except Exception as e:
        logger.error(f"Error in your mix endpoint: {str(e)}")
        return jsonify([]), 500

@app.route('/')
def index():
    logger.info("Received request for index route")
    return render_template('index.html')

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