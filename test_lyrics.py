
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
        
    headers = {
        "Authorization": f"Bearer {GENIUS_API_KEY}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"
    }
    
    # Test with specific song
    song_name = "Lock Sidhu Moose Wala"
    search_url = f"https://api.genius.com/search?q={song_name}"
    
    try:
        response = requests.get(search_url, headers=headers)
        print(f"\nAPI Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data["response"]["hits"]:
                for hit in data["response"]["hits"][:3]:  # Show top 3 results
                    print(f"\nFound: {hit['result']['full_title']}")
                    print(f"URL: {hit['result']['url']}")
                
                result = data["response"]["hits"][0]["result"]
                print("\n✅ API connection successful!")
                print(f"\nFirst result:")
                print(f"Title: {result['title']}")
                print(f"Artist: {result['primary_artist']['name']}")
                print(f"URL: {result['url']}")
                
                return data["response"]["hits"][0]
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
