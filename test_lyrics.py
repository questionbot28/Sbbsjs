
import os
import requests
from typing import Optional, Dict, Any

def test_genius_api() -> Optional[Dict[str, Any]]:
    GENIUS_API_KEY = os.getenv("GENIUS_API_KEY")
    
    if not GENIUS_API_KEY:
        print("❌ Genius API key not found! Please add it to Secrets.")
        return None
        
    headers = {"Authorization": f"Bearer {GENIUS_API_KEY}"}
    search_url = "https://api.genius.com/search"
    params = {"q": "Shape of You Ed Sheeran"}  # More specific search
    
    try:
        response = requests.get(search_url, headers=headers, params=params)
        response.raise_for_status()  # Raise exception for bad status codes
        
        data = response.json()
        if 'response' in data and 'hits' in data['response']:
            print("✅ API connection successful!")
            first_result = data['response']['hits'][0]['result']
            print(f"\nFirst result:")
            print(f"Title: {first_result['title']}")
            print(f"Artist: {first_result['primary_artist']['name']}")
            print(f"URL: {first_result['url']}")
            return data
            
        print("❌ Unexpected API response format")
        return None
        
    except requests.exceptions.RequestException as e:
        print(f"❌ API request failed: {str(e)}")
        return None

if __name__ == "__main__":
    test_genius_api()
