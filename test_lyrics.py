
import os
import requests
import json
from typing import Optional, Dict, Any

def test_genius_api() -> Optional[Dict[str, Any]]:
    """Test Genius API connectivity and search functionality"""
    GENIUS_API_KEY = os.getenv("GENIUS_API_KEY")
    
    if not GENIUS_API_KEY:
        print("❌ Genius API key not found! Please add it to Secrets.")
        return None
        
    headers = {"Authorization": f"Bearer {GENIUS_API_KEY}"}
    search_url = "https://api.genius.com/search"
    params = {"q": "Shape of You Ed Sheeran"}
    
    try:
        response = requests.get(search_url, headers=headers, params=params)
        print(f"\nAPI Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data["response"]["hits"]:
                result = data["response"]["hits"][0]["result"]
                print("\n✅ API connection successful!")
                print(f"\nFirst result:")
                print(f"Title: {result['title']}")
                print(f"Artist: {result['primary_artist']['name']}")
                print(f"URL: {result['url']}")
                
                # Get song details
                song_id = result['id']
                song_url = f"https://api.genius.com/songs/{song_id}"
                song_response = requests.get(song_url, headers=headers)
                print(f"\nSong API Response Status: {song_response.status_code}")
                
                if song_response.status_code == 200:
                    song_data = song_response.json()
                    return song_data
            else:
                print("❌ No results found")
                return None
        elif response.status_code == 401:
            print("❌ Authentication failed - Invalid API key")
        else:
            print(f"❌ API request failed: {response.status_code}")
            print(f"Response: {response.text}")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ API request failed: {str(e)}")
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing API response: {str(e)}")
    
    return None

if __name__ == "__main__":
    test_genius_api()
