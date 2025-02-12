import discord
from discord.ext import commands
import logging
import asyncio
from typing import Optional, Dict, Any, Union, List
import aiohttp
from bs4 import BeautifulSoup
import yt_dlp
import re
import random
from discord import SelectOption
from discord.ui import Select, View
import os
import lyricsgenius

class SongSelect(discord.ui.Select):
    def __init__(self, options: List[Dict[str, Any]], callback_func):
        super().__init__(
            placeholder="Choose a song to play...",
            min_values=1,
            max_values=1,
            options=[
                SelectOption(
                    label=f"{song['title'][:80]}", 
                    description=f"Duration: {song['duration_string']}",
                    value=str(i)
                ) for i, song in enumerate(options)
            ]
        )
        self.songs = options
        self.callback_func = callback_func

    async def callback(self, interaction: discord.Interaction):
        await self.callback_func(interaction, self.songs[int(self.values[0])])

class MusicCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger('discord_bot')
        self.voice_clients = {}
        self.current_tracks = {}
        self.volume = 1.0
        self.audio_filters = {
            'bassboost': 'bass=g=20:f=110:w=0.3',
            '8d': 'apulsator=hz=0.09',
            'nightcore': 'aresample=48000,asetrate=48000*1.25',
            'slowand_reverb': 'atempo=0.90,asetrate=44100*0.90,aecho=0.8:0.9:1000|1800:0.2|0.1,areverse,aecho=0.8:0.88:60|50:0.2|0.1,areverse'
        }
        self.progress_update_tasks = {}
        # Define mood playlists
        self.mood_playlists = {
            "happy": [
                "Don't Stop Believin' - Journey",
                "Happy - Pharrell Williams",
                "Uptown Funk - Bruno Mars",
                "Walking on Sunshine - Katrina & The Waves",
                "Good Vibrations - The Beach Boys"
            ],
            "sad": [
                "Someone Like You - Adele",
                "All By Myself - Celine Dion",
                "Yesterday - The Beatles",
                "Say Something - A Great Big World",
                "The Sound of Silence - Simon & Garfunkel"
            ],
            "chill": [
                "Waves - Mr Probz",
                "Stay With Me - Sam Smith",
                "Perfect - Ed Sheeran",
                "Better Together - Jack Johnson",
                "Sunday Morning - Maroon 5"
            ],
            "energetic": [
                "Eye of the Tiger - Survivor",
                "Stronger - Kanye West",
                "Can't Hold Us - Macklemore",
                "Thunderstruck - AC/DC",
                "All Star - Smash Mouth"
            ],
            "focus": [
                "River Flows in You - Yiruma",
                "Time - Hans Zimmer",
                "Experience - Ludovico Einaudi",
                "The Scientist - Coldplay",
                "Clocks - Coldplay"
            ]
        }
        # Initialize Genius API client only if key is available
        try:
            genius_token = os.getenv('GENIUS_API_KEY')
            if genius_token:
                self.genius = lyricsgenius.Genius(genius_token)
                self.genius.timeout = 15
                self.genius.retries = 3
                self.logger.info("Successfully initialized Genius API client")
            else:
                self.genius = None
                self.logger.info("Genius API key not found - lyrics features will be limited")
        except Exception as e:
            self.genius = None
            self.logger.warning(f"Could not initialize Genius API client: {str(e)}")

    async def get_lyrics(self, song_title: str, artist: str) -> Optional[str]:
        """Get lyrics for a song using Genius API and web scraping"""
        try:
            if not self.genius:
                self.logger.error("Genius API client not initialized")
                return None

            self.logger.info(f"Searching for lyrics: {song_title} by {artist}")
            
            # Search for song URL using Genius API
            # Use the Genius library's search method directly
            try:
                song = self.genius.search_song(song_title, artist)
                if song:
                    return song.lyrics
            except Exception as e:
                self.logger.error(f"Error searching with Genius library: {str(e)}")

            # Fallback to direct API if library search fails
            search_url = f"https://api.genius.com/search?q={song_title} {artist}"
            headers = {"Authorization": f"Bearer {os.getenv('GENIUS_API_KEY')}"}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(search_url, headers=headers) as response:
                    if response.status != 200:
                        return None
                    
                    data = await response.json()
                    if not data['response']['hits']:
                        return None
                    
                    song_url = data['response']['hits'][0]['result']['url']
                    
                    # Scrape lyrics from the Genius page
                    async with session.get(song_url) as page_response:
                        if page_response.status != 200:
                            return None
                            
                        html = await page_response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Try multiple methods to find lyrics
                        lyrics_div = soup.find("div", class_="lyrics")  # Old layout
                        if not lyrics_div:
                            lyrics_divs = soup.find_all("div", class_="Lyrics__Container")  # New layout
                            if lyrics_divs:
                                lyrics = "\n".join([div.get_text() for div in lyrics_divs])
                            else:
                                return f"[Click here to view lyrics]({song_url})"
                        else:
                            lyrics = lyrics_div.get_text()

                        # Clean up lyrics
                        lyrics = re.sub(r'[\(\[].*?[\)\]]', '', lyrics)  # Remove [Verse], [Chorus] etc
                        lyrics = re.sub(r'\n{3,}', '\n\n', lyrics)  # Remove extra newlines
                        lyrics = lyrics.strip()
                        
                        return lyrics.strip()

        except Exception as e:
            self.logger.error(f"Error getting lyrics: {str(e)}")
            return None

    @commands.command(name='getlyrics')
    async def get_lyrics_command(self, ctx, song_title: str, *, artist: str):
        """Get lyrics for a specific song"""
        loading_msg = await ctx.send(f"🔍 Searching lyrics for: {song_title} by {artist}...")

        self.logger.info(f"Searching lyrics - Title: {song_title}, Artist: {artist}")

        try:
            if not self.genius:
                await loading_msg.edit(content="❌ Genius API client not initialized. Please check API key.")
                return

            lyrics = await self.get_lyrics(song_title, artist)
            self.logger.info(f"Lyrics search result: {'Found' if lyrics else 'Not found'}")

            if not lyrics:
                await loading_msg.edit(content=(
                    "❌ No lyrics found. Please try:\n"
                    "• Using the exact song title\n"
                    "• Checking the artist name spelling\n"
                    "• Using quotation marks for titles with spaces"
                ))
                return

            # Clean up lyrics for better formatting
            lyrics = lyrics.strip()
            lyrics = re.sub(r'\n{3,}', '\n\n', lyrics)  # Replace multiple newlines with double newline

            # Create embed for song information
            embed = discord.Embed(
                title=f"🎵 {song_title}",
                color=discord.Color.blue()
            )
            embed.add_field(name="Artist", value=artist, inline=False)

            # Split lyrics into chunks of 2000 characters (Discord's limit)
            lyrics_chunks = [lyrics[i:i+2000] for i in range(0, len(lyrics), 2000)]

            # Send first chunk with song info
            first_chunk_embed = discord.Embed(
                title=f"🎵 {song_title} - {artist}",
                description=lyrics_chunks[0],
                color=discord.Color.blue()
            )
            await loading_msg.edit(content=None, embed=first_chunk_embed)

            # Send remaining chunks if any
            for chunk in lyrics_chunks[1:]:
                chunk_embed = discord.Embed(description=chunk, color=discord.Color.blue())
                await ctx.send(embed=chunk_embed)

        except Exception as e:
            self.logger.error(f"Error in get_lyrics_command: {str(e)}")
            await loading_msg.edit(content="❌ An error occurred while fetching lyrics.")

    def format_duration(self, seconds: int) -> str:
        """Format seconds into MM:SS"""
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"

    def create_progress_bar(self, current: int, total: int, length: int = 20) -> str:
        """Create a progress bar with specified length"""
        filled = int((current / total) * length)
        return f"▰{'▰' * filled}{'▱' * (length - filled)}"

    async def update_progress(self, ctx, message_id: int, track_info: Dict[str, Any]):
        """Update the progress bar for the currently playing song"""
        try:
            message = await ctx.channel.fetch_message(message_id)
            start_time = track_info['start_time']
            duration = track_info['duration']

            while ctx.voice_client and ctx.voice_client.is_playing():
                current_time = int(asyncio.get_event_loop().time() - start_time)
                if current_time >= duration:
                    break

                # Format timestamps
                current_timestamp = self.format_duration(current_time)
                duration_timestamp = self.format_duration(duration)

                # Calculate progress bar segments (20 segments total)
                progress = min(current_time / duration, 1.0)
                filled_segments = int(20 * progress)
                progress_bar = '▰' * filled_segments + '▱' * (20 - filled_segments)

                embed = message.embeds[0]
                embed.set_field_at(
                    0,  # Progress field is the first field
                    name="Progress",
                    value=f"{progress_bar}\n"
                          f"Time: `{current_timestamp} / {duration_timestamp}`\n"
                          f"Duration: `{duration_timestamp}`",
                    inline=False
                )

                try:
                    await message.edit(embed=embed)
                except discord.HTTPException as e:
                    self.logger.error(f"Error updating progress message: {e}")
                    break

                await asyncio.sleep(5)  # Update every 5 seconds

            # Final update to show completion
            if ctx.voice_client and not ctx.voice_client.is_playing():
                duration_timestamp = self.format_duration(duration)
                embed = message.embeds[0]
                embed.set_field_at(
                    0,
                    name="Progress",
                    value=f"{'▰' * 20}\n"
                          f"Time: `{duration_timestamp} / {duration_timestamp}`\n"
                          f"Duration: `{duration_timestamp}`",
                    inline=False
                )
                await message.edit(embed=embed)

        except Exception as e:
            self.logger.error(f"Error in progress update task: {str(e)}")

    async def get_song_results(self, query: str) -> List[Dict[str, Any]]:
        """Search for songs using yt-dlp"""
        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'default_search': 'ytsearch5',
            'simulate': True,
            'skip_download': True,
            'force_generic_extractor': False
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                self.logger.info(f"Searching for query: {query}")
                info = await asyncio.to_thread(ydl.extract_info, f"ytsearch5:{query}", download=False)
                if not info or 'entries' not in info:
                    self.logger.error("No search results found or invalid response format")
                    return []

                results = []
                for entry in info['entries'][:5]:
                    try:
                        # Store URL in track info for effect switching
                        url = entry.get('url', '') or entry.get('webpage_url', '')
                        if not url:
                            continue

                        result = {
                            'title': entry.get('title', 'Unknown Title'),
                            'url': url,
                            'webpage_url': entry.get('webpage_url', url),
                            'thumbnail': entry.get('thumbnail', ''),
                            'duration': int(entry.get('duration', 0)),
                            'duration_string': self.format_duration(int(entry.get('duration', 0))),
                            'uploader': entry.get('uploader', 'Unknown Artist')
                        }

                        results.append(result)

                    except Exception as e:
                        self.logger.error(f"Error processing search result: {str(e)}")
                        continue

                return results

        except Exception as e:
            self.logger.error(f"Error in song search: {str(e)}")
            return []

    @commands.command(name='play')
    async def play(self, ctx, *, query: str):
        """Play a song with selection menu"""
        if not ctx.author.voice:
            await ctx.send("❌ You need to be in a voice channel first!")
            return

        # Join voice channel if not already joined
        if ctx.guild.id not in self.voice_clients:
            channel = ctx.author.voice.channel
            try:
                voice_client = await channel.connect()
                self.voice_clients[ctx.guild.id] = voice_client
            except Exception as e:
                self.logger.error(f"Error joining voice channel: {e}")
                await ctx.send("❌ Could not join the voice channel.")
                return

        # Create initial search message with loading animation
        search_time = round(3.0 + random.uniform(0.1, 1.5), 1)  # Random time between 3-4.5s
        loading_msg = await ctx.send(
            f"🔍 **Finding the perfect match for:** `{query}`\n"
            f"⏳ Estimated Time: `{search_time}s`\n"
            "⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜  0%"
        )

        # Loading bar segments and their corresponding percentages
        loading_segments = [
            ("🟦⬜⬜⬜⬜⬜⬜⬜⬜⬜", "10%"),
            ("🟦🟦⬜⬜⬜⬜⬜⬜⬜⬜", "20%"),
            ("🟦🟦🟦⬜⬜⬜⬜⬜⬜⬜", "30%"),
            ("🟦🟦🟦🟦⬜⬜⬜⬜⬜⬜", "40%"),
            ("🟦🟦🟦🟦🟦⬜⬜⬜⬜⬜", "50%"),
            ("🟦🟦🟦🟦🟦🟦⬜⬜⬜⬜", "60%"),
            ("🟦🟦🟦🟦🟦🟦🟦⬜⬜⬜", "70%"),
            ("🟦🟦🟦🟦🟦🟦🟦🟦⬜⬜", "80%"),
            ("🟦🟦🟦🟦🟦🟦🟦🟦🟦⬜", "90%")
        ]

        # Animate loading bar while searching
        search_task = asyncio.create_task(self.get_song_results(query))

        for bar, percentage in loading_segments:
            try:
                await loading_msg.edit(
                    content=f"🔍 **Finding the perfect match for:** `{query}`\n"
                           f"⏳ Estimated Time: `{search_time}s`\n"
                           f"{bar}  {percentage}"
                )
                await asyncio.sleep(search_time / 10)  # Divide total time into 10 segments
            except discord.errors.NotFound:
                break  # Message was deleted

        # Get search results
        results = await search_task

        if not results:
            await loading_msg.edit(content="❌ No songs found!")
            return

        # Show completion message
        await loading_msg.edit(
            content=f"✅ **Match Found! Loading songs...** `100%`\n"
                   f"🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦  100%"
        )
        await asyncio.sleep(0.5)  # Brief pause to show completion

        # Create selection menu
        async def select_callback(interaction: discord.Interaction, song: Dict[str, Any]):
            if interaction.user.id != ctx.author.id:
                await interaction.response.send_message("❌ Only the requester can select a song!", ephemeral=True)
                return

            await interaction.response.defer()

            try:
                # Create embedded message for queue addition
                queue_embed = discord.Embed(
                    title="✅ Song Added to Queue",
                    description=f"**{song['title']}**\nBy: {song['uploader']}",
                    color=discord.Color.green()
                )
                if song['thumbnail']:
                    queue_embed.set_thumbnail(url=song['thumbnail'])
                await loading_msg.edit(content=None, embed=queue_embed, view=None)

                # Play the song
                voice_client = self.voice_clients[ctx.guild.id]

                # Setup FFmpeg options with filter if specified
                ffmpeg_options = {
                    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                    'options': '-vn'
                }

                # Add audio filter if specified in the query
                filter_keywords = ['bassboost', '8d', 'nightcore', 'slowand_reverb']
                applied_filter = next((f for f in filter_keywords if f in query.lower()), None)
                if applied_filter and applied_filter in self.audio_filters:
                    ffmpeg_options['options'] = f'-vn -af {self.audio_filters[applied_filter]}'
                    self.logger.info(f"Applying audio filter: {applied_filter} with options: {ffmpeg_options['options']}")

                # Create audio source
                try:
                    self.logger.info(f"Creating audio source with URL: {song['url']}")
                    audio_source = discord.FFmpegPCMAudio(song['url'], **ffmpeg_options)
                    voice_client.play(
                        discord.PCMVolumeTransformer(audio_source, volume=self.volume),
                        after=lambda e: asyncio.run_coroutine_threadsafe(
                            self.song_finished(ctx.guild.id, e), self.bot.loop
                        ) if e else None
                    )
                    self.logger.info("Successfully started playing audio")
                except Exception as e:
                    self.logger.error(f"Error creating audio source: {e}")
                    raise

                # Save current track info
                start_time = asyncio.get_event_loop().time()
                self.current_tracks[ctx.guild.id] = {
                    'title': song['title'],
                    'duration': song['duration'],
                    'thumbnail': song['thumbnail'],
                    'uploader': song['uploader'],
                    'requester': ctx.author,
                    'start_time': start_time,
                    'url': song['url']
                }

                # Create Now Playing embed
                playing_embed = discord.Embed(
                    title="🎵 Now Playing",
                    description=f"**{song['title']}**\nArtist: **{song['uploader']}**",
                    color=discord.Color.blue()
                )

                if song['thumbnail']:
                    playing_embed.set_thumbnail(url=song['thumbnail'])

                progress_bar = self.create_progress_bar(0, song['duration'])
                playing_embed.add_field(
                    name="Progress",
                    value=f"{progress_bar}\nTime: `00:00 / {song['duration_string']}`\nDuration: `{song['duration_string']}`",
                    inline=False
                )

                playing_embed.add_field(
                    name="Requested by",
                    value=ctx.author.mention,
                    inline=False
                )

                # Send and start progress updates
                now_playing_msg = await ctx.send(embed=playing_embed)

                # Cancel existing progress update task if any
                if ctx.guild.id in self.progress_update_tasks:
                    self.progress_update_tasks[ctx.guild.id].cancel()

                # Start new progress update task
                update_task = asyncio.create_task(
                    self.update_progress(ctx, now_playing_msg.id, self.current_tracks[ctx.guild.id])
                )
                self.progress_update_tasks[ctx.guild.id] = update_task

            except Exception as e:
                self.logger.error(f"Error playing song: {e}")
                await ctx.send("❌ An error occurred while playing the song.")

        # Create and send selection menu
        select_view = View()
        select_view.add_item(SongSelect(results, select_callback))
        await loading_msg.edit(content="Please select a song to play:", view=select_view)

    async def song_finished(self, guild_id: int, error):
        """Handle song finish event"""
        if error:
            self.logger.error(f"Error playing song: {error}")

        # Cancel progress update task
        if guild_id in self.progress_update_tasks:
            self.progress_update_tasks[guild_id].cancel()
            del self.progress_update_tasks[guild_id]

        if guild_id in self.current_tracks:
            del self.current_tracks[guild_id]

    @commands.command(name='pause')
    async def pause(self, ctx):
        """Pause the current song"""
        if ctx.guild.id in self.voice_clients:
            vc = self.voice_clients[ctx.guild.id]
            if vc.is_playing():
                vc.pause()
                await ctx.send("⏸️ Paused the current song")
            else:
                await ctx.send("❌ Nothing is playing!")
        else:
            await ctx.send("❌ I'm not in a voice channel!")

    @commands.command(name='resume')
    async def resume(self, ctx):
        """Resume the paused song"""
        if ctx.guild.id in self.voice_clients:
            vc = self.voice_clients[ctx.guild.id]
            if vc.is_paused():
                vc.resume()
                await ctx.send("▶️ Resumed the song")
            else:
                await ctx.send("❌ Nothing is paused!")
        else:
            await ctx.send("❌ I'm not in a voice channel!")

    @commands.command(name='stop')
    async def stop(self, ctx):
        """Stop playing and clear the queue"""
        if ctx.guild.id in self.voice_clients:
            vc = self.voice_clients[ctx.guild.id]
            if vc.is_playing() or vc.is_paused():
                vc.stop()
                await ctx.send("⏹️ Stopped playing")
            else:
                await ctx.send("❌ Nothing is playing!")
        else:
            await ctx.send("❌ I'm not in a voice channel!")

    @commands.command(name='musichelp')
    async def music_help(self, ctx):
        """Show all music-related commands"""
        embed = discord.Embed(
            title="🎵 Music Commands Help",
            description="Here are all the available music commands:",
            color=discord.Color.blue()
        )

        playback_commands = """
        `!join` - Join your voice channel
        `!play <song>` - Play a song
        `!moodplay <mood>` - Play music based on mood
        `!play <song> bassboost` - Play with bass boost
        `!play <song> 8d` - Play with 8D effect
        `!play <song> nightcore` - Play with nightcore effect
        `!play <song> slowand_reverb` - Play with slow + reverb effect
        `!pause` - Pause current song
        `!resume` - Resume paused song
        `!stop` - Stop playing
        `!volume <0-200>` - Adjust volume
        `!seek <forward/back> <seconds>` - Skip forward/backward in song
        `!normal` - Remove all audio effects
        """
        embed.add_field(
            name="🎧 Playback Commands",
            value=playback_commands,
            inline=False
        )

        mood_info = """
        Available moods for `!moodplay`:
        • `happy` - Upbeat and cheerful songs
        • `sad` - Emotional and melancholic tracks
        • `chill` - Relaxing and peaceful music
        • `energetic` - High-energy pump-up songs
        • `focus` - Concentration-enhancing tracks
        """
        embed.add_field(
            name="🎭 Mood Play",
            value=mood_info,
            inline=False
        )

        # Keep the rest of the help command unchanged
        audio_effects = """
        `!bassboost` - Apply bassboost effect
        `!8d` - Apply 8D effect
        `!nightcore` - Apply nightcore effect
        `!slowand_reverb` - Apply slow + reverb effect
        `!normal` - Remove all effects
        """
        embed.add_field(
            name="🎛️ Audio Effects",
            value=audio_effects,
            inline=False
        )

        examples = """
        • `!play Shape of You`
        • `!moodplay happy`
        • `!seek forward 30` - Skip forward 30 seconds
        • `!seek back 15` - Go back 15 seconds
        • `!play Blinding Lights slowand_reverb`
        """
        embed.add_field(
            name="📋 Examples",
            value=examples,
            inline=False
        )

        embed.set_footer(text="🎵 Enhanced Music Commands")
        await ctx.send(embed=embed)

    @commands.command(name='songinfo')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def songinfo(self, ctx, *, query: str):
        """Get detailed song information"""
        searching_embed = discord.Embed(
            title="🔍 Searching Song",
            description=f"Looking for: **{query}**",
            color=discord.Color.blue()
        )
        status_msg = await ctx.send(embed=searching_embed)

        try:
            result = await self.search_song_info(query)
            if not result:
                await status_msg.edit(embed=discord.Embed(
                    title="❌ Song Not Found",
                    description=f"Could not find information for '{query}'",
                    color=discord.Color.red()
                ))
                return

            info_embed = discord.Embed(
                title=f"📊 Song Details",
                color=discord.Color.blue()
            )

            info_embed.add_field(
                name="Title",
                value=result['title'],
                inline=True
            )

            if 'artist' in result:
                info_embed.add_field(
                    name="Artist",
                    value=result['artist'],
                    inline=True
                )

            info_embed.add_field(
                name="Source",
                value=result['source'],
                inline=True
            )

            info_embed.add_field(
                name="Links",
                value=f"[Listen/View]({result['url']})",
                inline=False
            )

            info_embed.set_footer(text="Type !musichelp for more commands")
            await status_msg.edit(embed=info_embed)

        except Exception as e:
            self.logger.error(f"Error in songinfo command: {str(e)}")
            await status_msg.edit(embed=discord.Embed(
                title="❌ Error",
                description="An error occurred while fetching song information.",
                color=discord.Color.red()
            ))

    async def search_song_info(self, query: str) -> Optional[Dict[str, Any]]:
        """Enhanced song search using multiple sources"""
        try:
            # Clean and format query with various search combinations
            base_term = query.strip().replace('"', '')  # Remove quotes
            search_terms = [
                base_term,                          # Original query
                base_term.lower(),                  # Lowercase
                base_term.title(),                  # Title case
                f"{base_term} lyrics",              # With 'lyrics'
                f"{base_term} YoungBoy",            # With artist name
                f"YoungBoy NBA {base_term}",        # Artist name first
                f"YoungBoy Never Broke Again {base_term}", # Full artist name
                base_term.replace(" ", ""),         # No spaces
                base_term.replace("'", "")          # Remove apostrophes
            ]

            # Convert terms to URL format
            urls = []
            for term in search_terms:
                url_term = term.replace(" ", "+")
                urls.extend([
                    f"https://search.azlyrics.com/search.php?q={url_term}",
                    f"https://search.azlyrics.com/suggest.php?q={url_term}"
                ])

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5'
            }

            async with aiohttp.ClientSession() as session:
                for url in urls:
                    try:
                        async with session.get(url, headers=headers, timeout=10) as response:
                            if response.status != 200:
                                self.logger.warning(f"Search failed for URL {url}: {response.status}")
                                continue

                            html = await response.text()
                            if "Please enable cookies" in html or "Access denied" in html:
                                self.logger.warning(f"Access restricted for {url}")
                                continue

                            soup = BeautifulSoup(html, 'html.parser')
                    except Exception as e:
                        self.logger.error(f"Error accessing URL {url}: {e}")
                        continue

                    # Search for song results
                    results = soup.find_all('td', class_='text-left visitedlyr')

                    if not results:
                        self.logger.info(f"No results found for query: {query}")
                        return None

                    # Get the first result
                    result = results[0]
                    song_link = result.find('a')
                    if not song_link:
                        return None

                    # Extract song info
                    title = song_link.get_text(strip=True)
                    artist = result.find_all('b')[-1].get_text(strip=True) if result.find_all('b') else "Unknown Artist"
                    url = song_link.get('href', '')

                    self.logger.info(f"Found song: {title} by {artist}")

                    return {
                        'title': title,
                        'artist': artist,
                        'url': url,
                        'source': 'AZLyrics',
                        'query': query
                    }

        except aiohttp.ClientError as e:
            self.logger.error(f"Network error in song search: {str(e)}")
            return None
        except Exception as e:
            self.logger.error(f"Error in song search: {str(e)}")
            return None

    @commands.command(name='lyrics')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def lyrics(self, ctx, *, query: str):
        """Get lyrics for a song"""
        loading_msg = await ctx.send("🔍 Searching for lyrics...")

        try:
            # Attempt to split the query into song title and artist
            parts = query.split(" - ")
            if len(parts) == 2:
                song_title, artist = parts
            else:
                song_title = query
                artist = ""

            self.logger.info(f"Searching lyrics - Title: {song_title}, Artist: {artist}")

            result = await self.search_song_info(query)

            if not result:
                await loading_msg.edit(content=(
                    "❌ No lyrics found. Please try:\n"
                    "• Using the format: song - artist\n"
                    "• Using the full song title\n"
                    "• Checking spelling"
                ))
                return

            embed = discord.Embed(
                title=f"🎵 {result['title']}",
                color=discord.Color.blue()
            )

            embed.add_field(
                name="Artist",
                value=result['artist'],
                inline=False
            )

            embed.add_field(
                name="Lyrics",
                value=f"[Click to view lyrics]({result['url']})",
                inline=False
            )

            await loading_msg.edit(content=None, embed=embed)

        except Exception as e:
            self.logger.error(f"Error in lyrics command: {str(e)}")
            await loading_msg.edit(content="❌ An error occurred while searching for lyrics.")    
    @commands.command(name='songlist')
    async def song_list(self, ctx, mood: str):
        """List songs available for a given mood"""
        if mood not in self.mood_playlists:
            await ctx.send(f"❌ Mood '{mood}' not found. Available moods: {', '.join(self.mood_playlists.keys())}")
            return

        embed = discord.Embed(
            title=f"🎵 {mood.title()} Mood Playlist",
            description="Here are some songs that match your mood:",
            color=discord.Color.blue()
        )

        # Add songs to embed
        songs_list = "\n".join([f"🎵 {i+1}. {song}" for i, song in enumerate(self.mood_playlists[mood])])
        embed.add_field(
            name="Songs",
            value=songs_list,
            inline=False
        )

        await ctx.send(embed=embed)

    @commands.command(name='moodplay')
    async def moodplay(self, ctx, mood: str):
        """Play music based on mood"""
        # Check if user is in a voice channel
        if not ctx.author.voice:
            await ctx.send("❌ You need to be in a voice channel first!")
            return

        # Clean up mood input and check validity
        mood = mood.lower().strip()
        if mood not in self.mood_playlists:
            available_moods = ", ".join(f"`{m}`" for m in self.mood_playlists.keys())
            await ctx.send(f"❌ Invalid mood. Available moods: {available_moods}")
            return

        # Get mood emoji
        mood_emojis = {
            "happy": "😊", "sad": "😢", "chill": "😌",
            "energetic": "⚡", "focus": "🎯"
        }
        emoji = mood_emojis.get(mood, "🎵")

        # Send initial message
        loading_msg = await ctx.send(f"{emoji} Finding the perfect **{mood}** song for you...")

        try:
            # Join voice channel if not already joined
            if ctx.guild.id not in self.voice_clients:
                try:
                    voice_client = await ctx.author.voice.channel.connect()
                    self.voice_clients[ctx.guild.id] = voice_client
                except Exception as e:
                    self.logger.error(f"Error joining voice channel: {e}")
                    await loading_msg.edit(content="❌ Could not join the voice channel.")
                    return

            # Select and get random song
            playlist = self.mood_playlists[mood]
            song_choice = random.choice(playlist)

            # Get song results
            results = await self.get_song_results(song_choice)
            if not results:
                await loading_msg.edit(content=f"❌ Could not find song: {song_choice}")
                return

            # Get first result
            song_info = results[0]

            # Play the song
            try:
                ffmpeg_options = {
                    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                    'options': '-vn'
                }
                audio_source = discord.FFmpegPCMAudio(song_info['url'], **ffmpeg_options)
                self.voice_clients[ctx.guild.id].play(
                    discord.PCMVolumeTransformer(audio_source, volume=self.volume),
                    after=lambda e: asyncio.run_coroutine_threadsafe(
                        self.song_finished(ctx.guild.id, e), self.bot.loop
                    ) if e else None
                )
            except Exception as e:
                self.logger.error(f"Error playing song: {e}")
                await loading_msg.edit(content="❌ Error playing the song. Please try again.")
                return

            # Update current track info
            self.current_tracks[ctx.guild.id] = {
                'title': song_info['title'],
                'duration': song_info['duration'],
                'thumbnail': song_info['thumbnail'],
                'uploader': song_info['uploader'],
                'requester': ctx.author,
                'start_time': asyncio.get_event_loop().time(),
                'url': song_info['url']
            }

            # Create and send Now Playing embed
            playing_embed = discord.Embed(
                title=f"{emoji} Now Playing ({mood.title()} Mood)",
                description=f"**{song_info['title']}**\nArtist: **{song_info['uploader']}**",
                color=discord.Color.blue()
            )

            if song_info['thumbnail']:
                playing_embed.set_thumbnail(url=song_info['thumbnail'])

            # Add progress information
            progress_bar = self.create_progress_bar(0, song_info['duration'])
            playing_embed.add_field(
                name="Progress",
                value=f"{progress_bar}\nTime: `00:00 / {song_info['duration_string']}`\nDuration: `{song_info['duration_string']}`",
                inline=False
            )

            playing_embed.add_field(
                name="Requested by",
                value=ctx.author.mention,
                inline=False
            )

            # Send embed and start progress updates
            now_playing_msg = await ctx.send(embed=playing_embed)
            await loading_msg.edit(content=f"{emoji} Playing a **{mood}** song: `{song_info['title']}`")

            # Update progress
            if ctx.guild.id in self.progress_update_tasks:
                self.progress_update_tasks[ctx.guild.id].cancel()

            self.progress_update_tasks[ctx.guild.id] = asyncio.create_task(
                self.update_progress(ctx, now_playing_msg.id, self.current_tracks[ctx.guild.id])
            )

        except Exception as e:
            self.logger.error(f"Error in moodplay command: {str(e)}")
            await loading_msg.edit(content=f"❌ An error occurred while playing the {mood} song. Please try again.")

    @commands.command(name='singer')
    async def singer(self, ctx, *, singer_name: str):
        """Play a random song from the specified singer"""
        if not ctx.author.voice:
            await ctx.send("❌ You need to be in a voice channel first!")
            return

        # Create initial search message
        loading_msg = await ctx.send(
            f"🎤 **Finding a song by:** `{singer_name}`\n"
            "🔍 Searching through artist's discography..."
        )

        try:
            # Format search query to focus on the singer
            search_query = f"{singer_name} official audio"
            self.logger.info(f"Searching for songs by: {singer_name}")

            # Get search results
            results = await self.get_song_results(search_query)

            if not results:
                await loading_msg.edit(content=f"❌ No songs found for **{singer_name}**!")
                return

            # Randomly select a song from the results
            song_info = random.choice(results)

            # Join voice channel if not already joined
            if ctx.guild.id not in self.voice_clients:
                try:
                    voice_client = await ctx.author.voice.channel.connect()
                    self.voice_clients[ctx.guild.id] = voice_client
                except Exception as e:
                    self.logger.error(f"Error joining voice channel: {e}")
                    await loading_msg.edit(content="❌ Could not join the voice channel.")
                    return

            # Setup FFmpeg options
            ffmpeg_options = {
                'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                'options': '-vn'
            }

            # Create and play audio
            try:
                audio_source = discord.FFmpegPCMAudio(song_info['url'], **ffmpeg_options)
                self.voice_clients[ctx.guild.id].play(
                    discord.PCMVolumeTransformer(audio_source, volume=self.volume),
                    after=lambda e: asyncio.run_coroutine_threadsafe(
                        self.song_finished(ctx.guild.id, e), self.bot.loop
                    ) if e else None
                )
            except Exception as e:
                self.logger.error(f"Error playing song: {e}")
                await loading_msg.edit(content="❌ Error playing the song. Please try again.")
                return

            # Update current track info
            self.current_tracks[ctx.guild.id] = {
                'title': song_info['title'],
                'duration': song_info['duration'],
                'thumbnail': song_info['thumbnail'],
                'uploader': song_info['uploader'],
                'requester': ctx.author,
                'start_time': asyncio.get_event_loop().time(),
                'url': song_info['url']
            }

            # Create Now Playing embed
            playing_embed = discord.Embed(
                title="🎤 Now Playing",
                description=f"**{song_info['title']}**\nBy: **{singer_name}**",
                color=discord.Color.blue()
            )

            if song_info['thumbnail']:
                playing_embed.set_thumbnail(url=song_info['thumbnail'])

            # Add progress information
            progress_bar = self.create_progress_bar(0, song_info['duration'])
            playing_embed.add_field(
                name="Progress",
                value=f"{progress_bar}\nTime: `00:00 / {song_info['duration_string']}`\nDuration: `{song_info['duration_string']}`",
                inline=False
            )

            playing_embed.add_field(
                name="Requested by",
                value=ctx.author.mention,
                inline=False
            )

            # Send Now Playing embed and update loading message
            now_playing_msg = await ctx.send(embed=playing_embed)

            # Delete the loading message instead of updating it
            await loading_msg.delete()

            # Update progress
            if ctx.guild.id in self.progress_update_tasks:
                self.progress_update_tasks[ctx.guild.id].cancel()

            self.progress_update_tasks[ctx.guild.id] = asyncio.create_task(
                self.update_progress(ctx, now_playing_msg.id, self.current_tracks[ctx.guild.id])
            )

        except Exception as e:
            self.logger.error(f"Error in singer command: {str(e)}")
            await loading_msg.edit(content=f"❌ An error occurred while playing songs by **{singer_name}**")

    @commands.command(name='vplay')
    async def vplay(self, ctx, *, query: str):
        """Start a YouTube watch party for a song"""
        if not ctx.author.voice:
            await ctx.send("❌ You need to be in a voice channel first!")
            return

        # Create initial search message
        loading_msg = await ctx.send(
            f"🔍 **Searching for:** `{query}`\n"
            "⏳ Setting up watch party..."
        )

        try:
            # Get search results using existing method
            results = await self.get_song_results(query)

            if not results:
                await loading_msg.edit(content="❌ No videos found!")
                return

            # Get the first result
            video = results[0]
            video_id = video['webpage_url'].split('watch?v=')[-1]

            # Check if user is in a valid voice channel
            if not ctx.author.voice or not ctx.author.voice.channel:
                await loading_msg.edit(content="❌ You need to be in a voice channel!")
                return

            # Create invite link with activity
            try:
                invite = await ctx.author.voice.channel.create_invite(
                    target_type=discord.InviteTarget.embedded_application,
                    target_application_id=880218394199220334,  # YouTube Watch Together App ID
                    max_age=86400  # 24 hours
                )

                # Create embedded message with video info and invite
                embed = discord.Embed(
                    title="🎥 YouTube Watch Party",
                    description=f"**{video['title']}**\nBy: {video['uploader']}",
                    color=discord.Color.red()
                )

                if video['thumbnail']:
                    embed.set_thumbnail(url=video['thumbnail'])

                embed.add_field(
                    name="Duration",
                    value=f"`{video['duration_string']}`",
                    inline=True
                )

                embed.add_field(
                    name="Host",
                    value=ctx.author.mention,
                    inline=True
                )

                embed.add_field(
                    name="How to Join",
                    value=f"1. Join the voice channel: {ctx.author.voice.channel.mention}\n"
                          f"2. Click the join button below\n"
                          f"3. The video will be preloaded: `{video['title']}`",
                    inline=False
                )

                # Create button for joining
                view = discord.ui.View()
                view.add_item(
                    discord.ui.Button(
                        style=discord.ButtonStyle.green,
                        label="Join Watch Party",
                        url=invite.url
                    )
                )

                # Send final message and delete loading message
                await ctx.send(embed=embed, view=view)
                await loading_msg.delete()

            except discord.errors.Forbidden:
                await loading_msg.edit(content="❌ I don't have permission to create invites!")
            except Exception as e:
                self.logger.error(f"Error creating watch party: {e}")
                await loading_msg.edit(content="❌ Failed to create watch party. Please try again.")

        except Exception as e:
            self.logger.error(f"Error in vplay command: {str(e)}")
            await loading_msg.edit(content="❌ An error occurred while setting up the watch party.")

    @commands.command(name='instant_lyrics')
    async def instant_lyrics(self, ctx):
        """Get lyrics for currently playing song"""
        try:
            if not ctx.voice_client or not ctx.voice_client.is_playing():
                await ctx.send("❌ No song is currently playing!")
                return

            current_song = ctx.voice_client.source.title
            self.logger.info(f"Searching for lyrics: {current_song}")

            search_url = f"https://api.genius.com/search?q={current_song}"
            headers = {"Authorization": f"Bearer {self.genius.auth.access_token}"}

            async with aiohttp.ClientSession() as session:
                async with session.get(search_url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data["response"]["hits"]:
                            song_url = data["response"]["hits"][0]["result"]["url"]
                            embed = discord.Embed(
                                title="📜 Lyrics Found!",
                                description=f"[Click here to view lyrics]({song_url})",
                                color=discord.Color.green()
                            )
                            embed.set_footer(text=f"Requested by {ctx.author.name}")
                            await ctx.send(embed=embed)
                        else:
                            await ctx.send("❌ No lyrics found for this song.")
                    else:
                        await ctx.send("❌ Failed to fetch lyrics.")
        except Exception as e:
            self.logger.error(f"Error getting lyrics: {str(e)}")
            await ctx.send("❌ Could not fetch lyrics at this time.")

async def setup(bot):
    await bot.add_cog(MusicCommands(bot))