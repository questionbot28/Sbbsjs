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
        # Initialize Genius API client with retries and timeout
        try:
            genius_token = os.getenv('GENIUS_API_KEY')
            if genius_token:
                self.genius = lyricsgenius.Genius(
                    genius_token,
                    timeout=15,
                    retries=3,
                    verbose=True,
                    remove_section_headers=True,
                    skip_non_songs=False
                )
                self.logger.info("Successfully initialized Genius API client")
            else:
                self.genius = None
                self.logger.error("Failed to initialize Genius API client - missing API key")
        except Exception as e:
            self.genius = None
            self.logger.error(f"Error initializing Genius API client: {str(e)}")

    async def get_lyrics(self, song_title: str, artist: str) -> Optional[str]:
        """Get lyrics for a song using Genius API via lyricsgenius library"""
        try:
            if not self.genius:
                self.logger.error("Genius API client not initialized")
                return None

            self.logger.info(f"Searching for lyrics: {song_title} by {artist}")

            # Try exact search first
            try:
                song = self.genius.search_song(f"{song_title}", artist)
            except Exception as search_error:
                self.logger.error(f"Error in initial search: {str(search_error)}")
                song = None

            if not song:
                self.logger.info(f"No results found with exact search, trying alternative search...")
                # Try alternative search formats
                search_attempts = [
                    (song_title, ""),  # Just the song title
                    (f"{song_title} {artist}", ""),  # Combined search
                    (song_title.lower(), artist.lower()),  # Lowercase everything
                ]

                for search_title, search_artist in search_attempts:
                    try:
                        song = self.genius.search_song(search_title, search_artist)
                        if song:
                            self.logger.info(f"Found lyrics with alternative search: {search_title} - {search_artist}")
                            break
                    except Exception as e:
                        self.logger.error(f"Error in alternative search: {str(e)}")
                        continue

            if song:
                self.logger.info(f"Found lyrics for: {song.title} by {song.artist}")
                return song.lyrics

            self.logger.warning(f"No lyrics found for: {song_title} by {artist} after all attempts")
            return None

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

            lyrics = await asyncio.to_thread(self.get_lyrics, song_title, artist)
            self.logger.info(f"Lyrics search result: {'Found' if lyrics else 'Not found'}")

            if not lyrics:
                song = await asyncio.to_thread(self.genius.search_song, song_title)
                if song and song.url:
                    await loading_msg.edit(content=(
                        f"📌 Lyrics available at: {song.url}\n\n"
                        "❌ Full lyrics not available. Please:\n"
                        "• Use the exact song title\n"
                        "• Check artist name spelling\n"
                        "• Use quotation marks for titles with spaces"
                    ))
                else:
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
            # Format query
            search_term = query.strip().replace(" ", "+")

            # Build URL with proper parameters
            url = f"https://search.azlyrics.com/search.php?q={search_term}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=10) as response:
                    if response.status != 200:
                        self.logger.error(f"Search API error: {response.status}")
                        return None

                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')

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

    @commands.command(name='join')
    async def join(self, ctx):
        """Join a voice channel"""
        if not ctx.author.voice:
            await ctx.send("❌ You need to be in a voice channel first!")
            return

        channel = ctx.author.voice.channel
        try:
            voice_client = await channel.connect()
            self.voice_clients[ctx.guild.id] = voice_client
            await ctx.send(f"✅ Joined {channel.name}")
        except Exception as e:
            self.logger.error(f"Error joining voice channel: {e}")
            await ctx.send("❌ Could not join the voice channel.")

    @commands.command(name='volume')
    async def volume(self, ctx, volume: float):
        """Change the volume of the currently playing song (0-200%)"""
        if not ctx.voice_client:
            await ctx.send("❌ I'm not in a voice channel!")
            return

        if not ctx.voice_client.is_playing():
            await ctx.send("❌ Nothing is playing right now!")
            return

        if not 0 <= volume <= 200:
            await ctx.send("❌ Volume must be between 0 and 200!")
            return

        try:
            ctx.voice_client.source.volume = volume / 100
            self.volume = volume / 100
            await ctx.send(f"🔊 Volume set to {volume}%")
            self.logger.info(f"Volume set to {volume}% for guild {ctx.guild.id}")
        except Exception as e:
            self.logger.error(f"Error setting volume: {str(e)}")
            await ctx.send("❌ An error occurred while adjusting the volume.")

    async def _apply_audio_effect(self, ctx: commands.Context, effect: str):
        """Apply an audio effect to the currently playing song"""
        if not ctx.voice_client or not ctx.voice_client.is_playing():
            await ctx.send("❌ Nothing is playing right now! Start a song first with !play")
            return

        if effect not in self.audio_filters:
            await ctx.send("❌ Invalid audio effect!")
            return

        try:
            if ctx.guild.id not in self.current_tracks:
                await ctx.send("❌ No track information available!")
                return

            track_info = self.current_tracks[ctx.guild.id]
            if 'url' not in track_info:
                await ctx.send("❌ Track URL not available!")
                return

            # Calculate current position
            current_time = int(asyncio.get_event_loop().time() - track_info['start_time'])

            # Log the effect application attempt
            self.logger.info(f"Applying {effect} effect at position {current_time}s")
            self.logger.info(f"Using filter: {self.audio_filters[effect]}")

            # Stop current playback
            ctx.voice_client.stop()

            # Create status message
            status_msg = await ctx.send(f"🎵 Applying {effect} effect...")

            try:
                # Setup FFmpeg options with enhanced filter chain
                ffmpeg_options = {
                    'before_options': f'-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -ss {current_time}',
                    'options': f'-vn -af "{self.audio_filters[effect]}"'
                }

                self.logger.debug(f"FFmpeg command options: {ffmpeg_options}")

                # Create new audio source with effect
                audio_source = discord.FFmpegPCMAudio(track_info['url'], **ffmpeg_options)
                transformed_source = discord.PCMVolumeTransformer(audio_source, volume=self.volume)

                # Update start time for progress tracking
                track_info['start_time'] = asyncio.get_event_loop().time() - current_time

                # Play with effect
                ctx.voice_client.play(
                    transformed_source,
                    after=lambda e: asyncio.run_coroutine_threadsafe(
                        self.song_finished(ctx.guild.id, e), self.bot.loop
                    ) if e else None
                )

                await status_msg.edit(content=f"✨ Applied {effect} effect to the current song!")
                self.logger.info(f"Successfully applied {effect} effect for guild {ctx.guild.id}")

            except Exception as audio_error:
                error_msg = str(audio_error)
                self.logger.error(f"FFmpeg error while applying effect: {error_msg}")
                self.logger.error(f"Full error details: {audio_error.__class__.__name__}: {error_msg}")

                await status_msg.edit(content="❌ Failed to apply audio effect. Please try again.")

                # Try to restore normal playback
                try:
                    audio_source = discord.FFmpegPCMAudio(
                        track_info['url'],
                        before_options=f'-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -ss {current_time}',
                        options='-vn'
                    )
                    ctx.voice_client.play(discord.PCMVolumeTransformer(audio_source, volume=self.volume))
                except Exception as restore_error:
                    self.logger.error(f"Error restoring playback: {restore_error}")

        except Exception as e:
            self.logger.error(f"Error applying audio effect: {str(e)}")
            await ctx.send("❌ An error occurred while applying the audio effect.")

    @commands.command(name='bassboost')
    async def bassboost(self, ctx):
        """Apply bassboost effect to the current song"""
        await self._apply_audio_effect(ctx, 'bassboost')

    @commands.command(name='8d')
    async def eight_d(self, ctx):
        """Apply 8D effect to the current song"""
        await self._apply_audio_effect(ctx, '8d')

    @commands.command(name='nightcore')
    async def nightcore(self, ctx):
        """Apply nightcore effect to the current song"""
        await self._apply_audio_effect(ctx, 'nightcore')

    @commands.command(name='slowand_reverb')
    async def slowand_reverb(self, ctx):
        """Apply slow + reverb effect to the current song"""
        try:
            # Adding detailed debug logging
            self.logger.info("Starting slow + reverb effect application")
            self.logger.info(f"Current filter chain: {self.audio_filters['slowand_reverb']}")

            # Additional checks
            if not ctx.voice_client:
                self.logger.error("No voice client found")
                await ctx.send("❌ Bot is not connected to a voice channel!")
                return

            if not ctx.voice_client.is_playing():
                self.logger.error("No audio currently playing")
                await ctx.send("❌ Nothing is playing right now!")
                return

            status_msg = await ctx.send("🎵 Applying slow + reverb effect...")

            # Apply the effect
            await self._apply_audio_effect(ctx, 'slowand_reverb')

            # Log success
            self.logger.info("Successfully applied slow + reverb effect")

        except Exception as e:
            self.logger.error(f"Error in slowand_reverb command: {str(e)}")
            self.logger.exception("Full traceback:")
            await ctx.send("❌ An error occurred while applying slow + reverb effect.")

    @commands.command(name='seek')
    async def seek(self, ctx, direction: str, seconds: int = 10):
        """Seek forward or backward in the current song
        Usage: !seek forward 30 or !seek back 15"""
        if not ctx.voice_client or not ctx.voice_client.is_playing():
            await ctx.send("❌ Nothing is playing right now!")
            return

        if ctx.guild.id not in self.current_tracks:
            await ctx.send("❌ No track information available!")
            return

        track_info = self.current_tracks[ctx.guild.id]
        current_time = int(asyncio.get_event_loop().time() - track_info['start_time'])

        # Calculate new position
        if direction.lower() in ['forward', 'f']:
            new_time = min(current_time + seconds, track_info['duration'])
        elif direction.lower() in ['back', 'b']:
            new_time = max(0, current_time - seconds)
        else:
            await ctx.send("❌ Invalid direction! Use 'forward' or'back'")
            return

        # Stop current playback
        ctx.voice_client.stop()

        # Setup FFmpeg options with new position
        ffmpeg_options = {
            'before_options': f'-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -ss {new_time}',
            'options': '-vn'
        }

        self.logger.info(f"Seeking to position {new_time}s")

        try:
            # Create new audio source
            audio_source = discord.FFmpegPCMAudio(track_info['url'], **ffmpeg_options)
            ctx.voice_client.play(
                discord.PCMVolumeTransformer(audio_source, volume=self.volume),
                after=lambda e: asyncio.run_coroutine_threadsafe(
                    self.song_finished(ctx.guild.id, e), self.bot.loop
                ) if e else None
            )

            await ctx.send(f"⏩ Seeked to position: {self.format_duration(new_time)}")

        except Exception as e:
            self.logger.error(f"Error seeking in track: {str(e)}")
            await ctx.send("❌ An error occurred while seeking.")

    @commands.command(name='aimashup')
    async def aimashup(self, ctx, *, songs: str):
        """Create an AI-powered mashup of two songs
        Usage: !aimashup "song1" | "song2"
        Example: !aimashup "Shape of You" | "Blinding Lights"
        """
        if not ctx.author.voice:
            await ctx.send("❌ You need to be in a voice channel first!")
            return

        # Split the songs
        try:
            song1, song2 = [s.strip().strip('"') for s in songs.split("|")]
        except ValueError:
            await ctx.send("❌ Please provide two songs separated by |")
            return

        # Create initial status message
        status_msg = await ctx.send(
            f"🤖 **AI is creating a mashup of:**\n"
            f"🎵 `{song1}`\n"
            f"🎵 `{song2}`\n\n"
            "⚙️ Processing... This may take a moment."
        )

        try:
            # Search for both songs
            song1_results = await self.get_song_results(song1)
            song2_results = await self.get_song_results(song2)

            if not song1_results or not song2_results:
                await status_msg.edit(content="❌ Couldn't find one or both songs!")
                return

            # Get the first result for each song
            song1_info = song1_results[0]
            song2_info = song2_results[0]

            # Update status
            await status_msg.edit(
                content=(
                    f"✨ **Creating AI Mashup**\n"
                    f"🎵 Found: `{song1_info['title']}`\n"
                    f"🎵 Found: `{song2_info['title']}`\n\n"
                    "🔄 Downloading and mixing songs..."
                )
            )

            # Join voice channel if not already joined
            if ctx.guild.id not in self.voice_clients:
                try:
                    voice_client = await ctx.author.voice.channel.connect()
                    self.voice_clients[ctx.guild.id] = voice_client
                except Exception as e:
                    self.logger.error(f"Error joining voice channel: {e}")
                    await status_msg.edit(content="❌ Could not join the voice channel.")
                    return

            try:
                # Create audio source with basic mixing filter
                audio_source = discord.FFmpegPCMAudio(
                    song1_info['url'],
                    before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                    options='-vn -af asetrate=44100,aresample=44100,volume=0.5'
                )

                # Save current track info
                self.current_tracks[ctx.guild.id] = {
                    'title': f"Mashup: {song1_info['title']} × {song2_info['title']}",
                    'duration': max(song1_info['duration'], song2_info['duration']),
                    'thumbnail': song1_info['thumbnail'],
                    'requester': ctx.author,
                    'start_time': asyncio.get_event_loop().time(),
                    'url': song1_info['url']
                }

                # Play first song
                self.voice_clients[ctx.guild.id].play(
                    discord.PCMVolumeTransformer(audio_source, volume=self.volume),
                    after=lambda e: asyncio.run_coroutine_threadsafe(
                        self._play_second_track(ctx.guild.id, song2_info, e), self.bot.loop
                    ) if e else None
                )

                # Create mashup embed
                mashup_embed = discord.Embed(
                    title="🎵 AI Mashup Playing",
                    description=(
                        f"**Mixing:**\n"
                        f"1️⃣ {song1_info['title']}\n"
                        f"2️⃣ {song2_info['title']}"
                    ),
                    color=discord.Color.blue()
                )
                mashup_embed.add_field(
                    name="Created By",
                    value=ctx.author.mention,
                    inline=True
                )
                mashup_embed.set_footer(text="🤖 AI-Powered Mashup")

                await status_msg.edit(content=None, embed=mashup_embed)

            except Exception as e:
                self.logger.error(f"Error creating mashup: {e}")
                await status_msg.edit(content="❌ An error occurred while creating the mashup.")
                return

        except Exception as e:
            self.logger.error(f"Error in aimashup command: {e}")
            await status_msg.edit(content="❌ An error occurred while processing your request.")

    async def _play_second_track(self, guild_id: int, song_info: dict, error):
        """Helper method to play the second track in the mashup"""
        if error:
            self.logger.error(f"Error in first track: {error}")
            return

        try:
            # Create audio source for second song
            audio_source = discord.FFmpegPCMAudio(
                song_info['url'],
                before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                options='-vn -af asetrate=44100,aresample=44100,volume=0.5'
            )

            # Play second song
            if guild_id in self.voice_clients and self.voice_clients[guild_id]:
                self.voice_clients[guild_id].play(
                    discord.PCMVolumeTransformer(audio_source, volume=self.volume),
                    after=lambda e: asyncio.run_coroutine_threadsafe(
                        self.song_finished(guild_id, e), self.bot.loop
                    ) if e else None
                )
        except Exception as e:
            self.logger.error(f"Error playing second track: {e}")

    @commands.command(name='normal')
    async def remove_effects(self, ctx):
        """Remove all audio effects and return to normal playback"""
        if not ctx.voice_client or not ctx.voice_client.is_playing():
            await ctx.send("❌ Nothing is playing right now!")
            return

        if ctx.guild.id not in self.current_tracks:
            await ctx.send("❌ No track information available!")
            return

        track_info = self.current_tracks[ctx.guild.id]
        current_time = int(asyncio.get_event_loop().time() - track_info['start_time'])

        try:
            # Stop current playback
            ctx.voice_client.stop()

            # Setup normal FFmpeg options
            ffmpeg_options = {
                'before_options': f'-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -ss {current_time}',
                'options': '-vn'
            }

            # Create new audio source without effects
            audio_source = discord.FFmpegPCMAudio(track_info['url'], **ffmpeg_options)
            transformed_source = discord.PCMVolumeTransformer(audio_source, volume=self.volume)

            # Update start time for progress tracking
            track_info['start_time'] = asyncio.get_event_loop().time() - current_time

            # Play without effects
            ctx.voice_client.play(
                transformed_source,
                after=lambda e: asyncio.run_coroutine_threadsafe(
                    self.song_finished(ctx.guild.id, e), self.bot.loop
                ) if e else None
            )

            await ctx.send("✨ Removed all audio effects!")

        except Exception as e:
            self.logger.error(f"Error removing audio effects: {str(e)}")
            await ctx.send("❌ An error occurred while removing the audio effects.")


    @commands.command(name='vplay', aliases=['videoplay'])
    async def vplay(self, ctx, *, query: str):
        """Enhanced voice channel play command with automatic connection handling"""
        if not ctx.author.voice:
            await ctx.send("❌ You need to be in a voice channel first!")
            return

        # Create initial search message with loading animation
        loading_msg = await ctx.send(
            f"🔍 **Finding your song:** `{query}`\n"
            "⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜  0%"
        )

        try:
            # Search for song
            results = await self.get_song_results(query)
            if not results:
                await loading_msg.edit(content="❌ No songs found!")
                return

            song_info = results[0]  # Get first result for direct play

            # Connect to voice channel if not already connected
            if not ctx.voice_client:
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

                # Save current track info
                start_time = asyncio.get_event_loop().time()
                self.current_tracks[ctx.guild.id] = {
                    'title': song_info['title'],
                    'duration': song_info['duration'],
                    'thumbnail': song_info['thumbnail'],
                    'uploader': song_info['uploader'],
                    'requester': ctx.author,
                    'start_time': start_time,
                    'url': song_info['url']
                }

                # Create Now Playing embed
                playing_embed = discord.Embed(
                    title="🎵 Now Playing",
                    description=f"**{song_info['title']}**\nArtist: **{song_info['uploader']}**",
                    color=discord.Color.blue()
                )

                if song_info['thumbnail']:
                    playing_embed.set_thumbnail(url=song_info['thumbnail'])

                progress_bar = self.create_progress_bar(0, song_info['duration'])
                playing_embed.add_field(
                    name="Progress",
                    value=f"{progress_bar}\nTime: `00:00 / {song_info['duration_string']}`\n"
                          f"Duration: `{song_info['duration_string']}`",
                    inline=False
                )

                playing_embed.add_field(
                    name="Requested by",
                    value=ctx.author.mention,
                    inline=False
                )

                # Send and start progress updates
                now_playing_msg = await ctx.send(embed=playing_embed)

                # Start progress update task
                if ctx.guild.id in self.progress_update_tasks:
                    self.progress_update_tasks[ctx.guild.id].cancel()

                update_task = asyncio.create_task(
                    self.update_progress(ctx, now_playing_msg.id, self.current_tracks[ctx.guild.id])
                )
                self.progress_update_tasks[ctx.guild.id] = update_task

                # Delete the loading message
                await loading_msg.delete()

            except Exception as e:
                self.logger.error(f"Error playing song in vplay: {e}")
                await loading_msg.edit(content="❌ An error occurred while playing the song.")

        except Exception as e:
            self.logger.error(f"Error in vplay command: {e}")
            await loading_msg.edit(content="❌ An error occurred while processing your request.")

    async def get_lyrics(self, song_title: str, artist: str) -> Optional[str]:
        """Get lyrics for a song using Genius API"""
        try:
            if not self.genius:
                self.logger.error("Genius client not initialized")
                return None
                
            search_term = f"{song_title} {artist}".strip()
            self.logger.info(f"Searching for lyrics: {search_term}")
            
            song = await asyncio.to_thread(
                self.genius.search_song,
                search_term,
                get_full_info=True,
                sanitize=True
            )
            
            if song and song.lyrics:
                # Clean up lyrics
                lyrics = song.lyrics.strip()
                # Remove Genius-specific text if present
                lyrics = lyrics.replace('Lyrics', '').replace('Embed', '')
                return lyrics
                
            self.logger.warning(f"No lyrics found for: {search_term}")
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting lyrics: {e}")
            return None


    @commands.command(name='getlyrics')
    async def get_lyrics_command(self, ctx, song_title: str, *, artist: str):
        """Get lyrics for a specific song"""
        loading_msg = await ctx.send(f"🔍 Searching lyrics for: {song_title} by {artist}...")

        try:
            lyrics = await self.get_lyrics(song_title, artist)

            if not lyrics:
                await loading_msg.edit(content=(
                    "❌ No lyrics found. Please try:\n"
                    "• Using the exact song title\n"
                    "• Checking the artist name spelling\n"
                    "• Using quotation marks for titles with spaces"
                ))
                return

            if isinstance(lyrics, str):
                # Clean up lyrics for better formatting
                lyrics = lyrics.strip()
                lyrics = re.sub(r'\n{3,}', '\n\n', lyrics)  # Replace multiple newlines with double newline
            else:
                await loading_msg.edit(content="❌ Error processing lyrics response")
                return

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

async def setup(bot):
    await bot.add_cog(MusicCommands(bot))