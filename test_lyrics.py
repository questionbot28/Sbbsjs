import os
import json
import aiohttp
import asyncio
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_spotify_musixmatch_api():
    """Test Spotify and Musixmatch API integration"""
    try:
        # Test song
        song_name = "Lock"
        artist_name = "Sidhu Moose Wala"

        print(f"\nTesting lyrics fetch for: {song_name} by {artist_name}")

        # Get Spotify token
        auth_url = "https://accounts.spotify.com/api/token"
        auth_data = {
            "grant_type": "client_credentials",
            "client_id": os.getenv('SPOTIFY_CLIENT_ID'),
            "client_secret": os.getenv('SPOTIFY_CLIENT_SECRET')
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(auth_url, data=auth_data) as auth_response:
                if auth_response.status != 200:
                    print("❌ Failed to get Spotify token")
                    return

                token_data = await auth_response.json()
                access_token = token_data["access_token"]
                print("✅ Got Spotify access token")

                # Search on Spotify
                search_url = f"https://api.spotify.com/v1/search?q={song_name}%20{artist_name}&type=track"
                headers = {"Authorization": f"Bearer {access_token}"}

                async with session.get(search_url, headers=headers) as spotify_response:
                    spotify_data = await spotify_response.json()
                    if "tracks" not in spotify_data or not spotify_data["tracks"]["items"]:
                        print("❌ Song not found on Spotify")
                        return

                    track = spotify_data["tracks"]["items"][0]
                    print(f"\n✅ Found on Spotify:")
                    print(f"Title: {track['name']}")
                    print(f"Artist: {track['artists'][0]['name']}")

                    # Get Musixmatch lyrics
                    musixmatch_key = os.getenv('MUSIXMATCH_API_KEY')
                    lyrics_url = "https://api.musixmatch.com/ws/1.1/matcher.lyrics.get"
                    params = {
                        "q_track": track['name'],
                        "q_artist": track['artists'][0]['name'],
                        "apikey": musixmatch_key
                    }

                    async with session.get(lyrics_url, params=params) as lyrics_response:
                        lyrics_data = await lyrics_response.json()
                        if "message" in lyrics_data and "body" in lyrics_data["message"]:
                            lyrics = lyrics_data["message"]["body"]["lyrics"]["lyrics_body"]
                            print("\n✅ Found lyrics! First few lines:")
                            preview = "\n".join(lyrics.split("\n")[:5])
                            print(f"{preview}...")
                        else:
                            print("❌ No lyrics found")
    except Exception as e:
        print(f"Error in test_spotify_musixmatch_api: {e}")

async def test_musixmatch_api():
    """Test Musixmatch API integration with improved error handling"""
    try:
        # Test song
        song_name = "Shape of You"
        artist_name = "Ed Sheeran"

        print(f"\nTesting lyrics fetch for: {song_name} by {artist_name}")

        musixmatch_key = os.getenv('MUSIXMATCH_API_KEY')
        if not musixmatch_key:
            print("❌ Musixmatch API key not found in environment variables")
            return

        # Prepare request
        lyrics_url = "https://api.musixmatch.com/ws/1.1/matcher.lyrics.get"
        params = {
            "q_track": song_name,
            "q_artist": artist_name,
            "apikey": musixmatch_key,
            "format": "json"  # Force JSON response
        }
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "EducationalBot/1.0"
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(lyrics_url, params=params, headers=headers) as response:
                # Log raw response for debugging
                raw_response = await response.text()
                print(f"\nAPI Response Status: {response.status}")
                print(f"Raw Response Preview: {raw_response[:200]}...")

                if response.status == 429:
                    print("❌ Rate limit reached. Please wait before trying again.")
                    return

                if response.status != 200:
                    print(f"❌ HTTP Error {response.status}")
                    return

                try:
                    data = json.loads(raw_response)
                    status_code = data['message']['header']['status_code']

                    if status_code != 200:
                        print(f"❌ API Error {status_code}: {data['message']['header'].get('message', 'Unknown error')}")
                        return

                    lyrics = data['message']['body']['lyrics']['lyrics_body']
                    preview = "\n".join(lyrics.split("\n")[:5])
                    print("\n✅ Successfully retrieved lyrics! Preview:")
                    print(f"{preview}...")

                except json.JSONDecodeError as e:
                    print(f"❌ JSON Parse Error: {str(e)}")
                    print(f"Raw Response: {raw_response}")
                except KeyError as e:
                    print(f"❌ Unexpected API Response Format: {str(e)}")
                    print(f"Response Data: {json.dumps(data, indent=2)}")

    except Exception as e:
        print(f"❌ Error in test_musixmatch_api: {str(e)}")

async def main():
    await test_spotify_musixmatch_api()
    await test_musixmatch_api()

if __name__ == "__main__":
    asyncio.run(main())