
import os
import lyricsgenius

genius_token = os.getenv('GENIUS_API_KEY')
if not genius_token:
    print("❌ Genius API key not found! Please add it to Secrets.")
    exit()

genius = lyricsgenius.Genius(genius_token)
song = genius.search_song("Shape of You", "Ed Sheeran")

if song:
    print("✅ Lyrics found!")
    print("\n" + "="*50 + "\n")
    print(song.lyrics[:1000])  # Print first 1000 characters
    print("\n" + "="*50 + "\n")
else:
    print("❌ Lyrics not found")
