import os
import aiohttp
import asyncio
from typing import Optional, Dict, Any

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
                    lyrics_url = f"https://api.musixmatch.com/ws/1.1/matcher.lyrics.get"
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

if __name__ == "__main__":
    asyncio.run(test_spotify_musixmatch_api())

async def test_musixmatch_api():
    """Test Musixmatch API integration"""
    try:
        # Test song
        song_name = "Shape of You"
        artist_name = "Ed Sheeran"

        print(f"\nTesting lyrics fetch for: {song_name} by {artist_name}")

        musixmatch_key = os.getenv('MUSIXMATCH_API_KEY')
        if not musixmatch_key:
            print("❌ Musixmatch API key not found in environment variables")
            return

        # Get lyrics from Musixmatch
        lyrics_url = "https://api.musixmatch.com/ws/1.1/matcher.lyrics.get"
        params = {
            "q_track": song_name,
            "q_artist": artist_name,
            "apikey": musixmatch_key
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(lyrics_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if "message" in data and "body" in data["message"]:
                        lyrics = data["message"]["body"]["lyrics"]["lyrics_body"]
                        print("\n✅ Found lyrics! First few lines:")
                        preview = "\n".join(lyrics.split("\n")[:5])
                        print(f"{preview}...")
                    else:
                        print("❌ No lyrics found")
                else:
                    print(f"❌ API request failed with status: {response.status}")

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    asyncio.run(test_spotify_musixmatch_api())
    asyncio.run(test_musixmatch_api())