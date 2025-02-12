import os
import lyricsgenius
from typing import Optional

def test_genius_api():
    """Test Genius API connectivity and search functionality"""
    GENIUS_API_KEY = os.getenv("GENIUS_API_KEY")

    if not GENIUS_API_KEY:
        print("❌ Genius API key not found! Please add it to Secrets.")
        return None

    try:
        genius = lyricsgenius.Genius(GENIUS_API_KEY)
        genius.timeout = 15  # Set timeout for requests
        genius.retries = 3   # Number of retries if request fails

        # Test with specific song
        song_name = "Lock"
        artist_name = "Sidhu Moose Wala"

        print(f"\nSearching for: {song_name} by {artist_name}")

        song = genius.search_song(song_name, artist_name)

        if song:
            print("\n✅ Song found!")
            print(f"Title: {song.title}")
            print(f"Artist: {song.artist}")
            print(f"URL: {song.url}")

            if song.lyrics:
                print("\n✅ Lyrics found!")
                print("\nFirst few lines:")
                lyrics_preview = "\n".join(song.lyrics.split("\n")[:5])
                print(f"{lyrics_preview}...")
                return song
            else:
                print("❌ No lyrics found")
                return None
        else:
            print("❌ Song not found")
            return None

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

if __name__ == "__main__":
    test_genius_api()