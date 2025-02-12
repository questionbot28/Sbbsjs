import os
import requests
import json
from typing import Optional, Dict, Any
from bs4 import BeautifulSoup

def scrape_lyrics(song_url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"
    }

    print("Attempting to scrape lyrics...")
    response = requests.get(song_url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    # Try multiple methods to find lyrics
    lyrics = None

    # Method 1: Check for old Genius format
    lyrics_div = soup.find("div", class_="lyrics")
    if lyrics_div:
        lyrics = lyrics_div.get_text()

    # Method 2: Check for new Genius format
    if not lyrics:
        lyrics_divs = soup.find_all("div", class_="Lyrics__Container")
        if lyrics_divs:
            lyrics = "\n".join([div.get_text(separator="\n") for div in lyrics_divs])

    # Method 3: Try finding other possible classes
    if not lyrics:
        lyrics_divs = soup.find_all("div", class_="lyric-text")
        if lyrics_divs:
            lyrics = "\n".join([div.get_text(separator="\n") for div in lyrics_divs])

    if lyrics:
        print("✅ Lyrics scraped successfully!")
        return lyrics.strip()
    else:
        print("❌ Could not scrape lyrics.")
        return f"Lyrics not available! Check here: {song_url}"

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
                first_hit = data["response"]["hits"][0]["result"]
                print("\n✅ API connection successful!")
                print(f"\nFirst result:")
                print(f"Title: {first_hit['title']}")
                print(f"Artist: {first_hit['primary_artist']['name']}")
                print(f"URL: {first_hit['url']}")
                
                # Try to scrape lyrics
                print("\nAttempting to scrape lyrics...")
                lyrics = scrape_lyrics(first_hit['url'])
                if lyrics:
                    print("\n✅ Lyrics found!")
                    print("\nFirst few lines:")
                    print("\n".join(lyrics.split("\n")[:5]) + "...")
                else:
                    print("❌ Could not scrape lyrics")
                
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