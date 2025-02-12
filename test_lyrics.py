
import os
import aiohttp
import asyncio
from typing import Optional, Dict, Any

async def test_jiosaavn_api():
    """Test JioSaavn API connectivity and search functionality"""
    try:
        # Test with specific song
        song_name = "Lock"
        artist_name = "Sidhu Moose Wala"
        search_query = f"{song_name} {artist_name}"

        print(f"\nSearching for: {search_query}")

        # First get song ID from search
        search_url = f"https://saavn.dev/api/search?query={search_query}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(search_url) as response:
                if response.status != 200:
                    print(f"❌ API request failed: {response.status}")
                    return None

                data = await response.json()
                if not data.get('results'):
                    print("❌ No results found")
                    return None

                # Get first result
                song = data['results'][0]
                print("\n✅ Song found!")
                print(f"Title: {song.get('title')}")
                print(f"Artist: {song.get('artist')}")
                print(f"URL: {song.get('url')}")

                # Try to get lyrics
                song_id = song.get('id')
                if song_id:
                    lyrics_url = f"https://saavn.dev/api/lyrics/{song_id}"
                    async with session.get(lyrics_url) as lyrics_response:
                        if lyrics_response.status == 200:
                            lyrics_data = await lyrics_response.json()
                            if lyrics_data.get('lyrics'):
                                print("\n✅ Lyrics found!")
                                print("\nFirst few lines:")
                                lyrics_preview = "\n".join(lyrics_data['lyrics'].split("\n")[:5])
                                print(f"{lyrics_preview}...")
                                return lyrics_data
                            else:
                                print("❌ No lyrics found")
                                return None
                        else:
                            print(f"❌ Failed to fetch lyrics: {lyrics_response.status}")
                            return None

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

if __name__ == "__main__":
    asyncio.run(test_jiosaavn_api())
