import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key
MUSIXMATCH_API_KEY = os.getenv('MUSIXMATCH_API_KEY')

def test_musixmatch():
    # First verify if we have the API key
    if not MUSIXMATCH_API_KEY:
        print("❌ Error: MUSIXMATCH_API_KEY not found in environment variables")
        return False

    print(f"API Key length: {len(MUSIXMATCH_API_KEY)} characters")  # Just print length for security

    # Use track.search endpoint which is commonly used for testing
    url = f"https://api.musixmatch.com/ws/1.1/track.search"
    params = {
        'apikey': MUSIXMATCH_API_KEY,
        'q_track': 'yesterday',
        'q_artist': 'beatles',
        'page_size': 1,
        'page': 1,
        'f_has_lyrics': 1
    }

    try:
        response = requests.get(url, params=params)
        print(f"Status Code: {response.status_code}")
        data = response.json()

        if "message" in data:
            status_code = data["message"]["header"]["status_code"]
            print(f"API Status Code: {status_code}")

            if status_code == 200:
                print("✅ Musixmatch API is working!")
                return True
            else:
                print("❌ API error:", data)
                return False
    except Exception as e:
        print(f"❌ Exception occurred: {str(e)}")
        return False

if __name__ == "__main__":
    test_musixmatch()