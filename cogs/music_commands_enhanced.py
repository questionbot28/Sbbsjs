import discord
from discord.ext import commands
import logging
import asyncio
from typing import Optional, Dict, Any, Union, List
import aiohttp
from bs4 import BeautifulSoup
import yt_dlp
import re
from discord import SelectOption
from discord.ui import Select, View

class SongSelect(discord.ui.Select):
    def __init__(self, options: List[Dict[str, Any]], callback_func):
        super().__init__(
            placeholder="Choose a song to play...",
            min_values=1,
            max_values=1,
            options=[
                SelectOption(
                    label=f"{song['title'][:80]}",  # Truncate long titles
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
    """Music commands using enhanced web scraping and playback"""

    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger('discord_bot')
        self.search_url = "https://search.azlyrics.com/search.php"
        self.voice_clients = {}
        self.current_tracks = {}
        self.volume = 1.0
        self.audio_filters = {
            'bassboost': 'bass=g=20:f=110:w=0.3',
            '8d': 'apulsator=hz=0.09',
            'nightcore': 'aresample=48000,asetrate=48000*1.25',
            'reverb': 'aecho=0.8:0.9:1000:0.3'
        }
        self.progress_update_tasks = {}

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
                current_time = asyncio.get_event_loop().time() - start_time
                if current_time >= duration:
                    break

                progress_bar = self.create_progress_bar(int(current_time), duration)
                current_timestamp = self.format_duration(int(current_time))
                duration_timestamp = self.format_duration(duration)

                embed = message.embeds[0]
                for field in embed.fields:
                    if field.name == "Progress":
                        field.value = (
                            f"{progress_bar}\n"
                            f"Time: `{current_timestamp} / {duration_timestamp}`\n"
                            f"Duration: `{duration_timestamp}`"
                        )
                        break

                await message.edit(embed=embed)
                await asyncio.sleep(5)  # Update every 5 seconds

        except Exception as e:
            self.logger.error(f"Error updating progress: {e}")

    async def get_song_results(self, query: str) -> List[Dict[str, Any]]:
        """Search for songs using yt-dlp"""
        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
            'default_search': 'ytsearch5'  # Get top 5 results
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = await asyncio.to_thread(ydl.extract_info, f"ytsearch5:{query}", download=False)
                if not info.get('entries'):
                    return []

                results = []
                for entry in info['entries'][:5]:  # Limit to 5 results
                    duration = int(entry.get('duration', 0))
                    results.append({
                        'title': entry['title'],
                        'url': entry['url'],
                        'webpage_url': entry['webpage_url'],
                        'thumbnail': entry.get('thumbnail', ''),
                        'duration': duration,
                        'duration_string': self.format_duration(duration),
                        'uploader': entry.get('uploader', 'Unknown Artist')
                    })
                return results

        except Exception as e:
            self.logger.error(f"Error searching songs: {e}")
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

        # Search for songs
        loading_msg = await ctx.send("🔍 Searching for songs...")
        results = await self.get_song_results(query)

        if not results:
            await loading_msg.edit(content="❌ No songs found!")
            return

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
                filter_keywords = ['bassboost', '8d', 'nightcore', 'reverb']
                applied_filter = next((f for f in filter_keywords if f in query.lower()), None)
                if applied_filter and applied_filter in self.audio_filters:
                    ffmpeg_options['options'] = f'-vn -af {self.audio_filters[applied_filter]}'

                # Create audio source
                audio_source = discord.FFmpegPCMAudio(song['url'], **ffmpeg_options)
                voice_client.play(
                    discord.PCMVolumeTransformer(audio_source, volume=self.volume),
                    after=lambda e: asyncio.run_coroutine_threadsafe(
                        self.song_finished(ctx.guild.id, e), self.bot.loop
                    ) if e else None
                )

                # Save current track info
                start_time = asyncio.get_event_loop().time()
                self.current_tracks[ctx.guild.id] = {
                    'title': song['title'],
                    'duration': song['duration'],
                    'thumbnail': song['thumbnail'],
                    'uploader': song['uploader'],
                    'requester': ctx.author,
                    'start_time': start_time
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
        `!play <song> reverb` - Play with reverb effect
        `!pause` - Pause current song
        `!resume` - Resume paused song
        `!stop` - Stop playing
        """
        embed.add_field(
            name="🎧 Playback Commands",
            value=playback_commands,
            inline=False
        )

        lyrics_commands = """
        `!lyrics <song> - <artist>` - Search for song lyrics
        `!songinfo <song>` - Get song information
        """
        embed.add_field(
            name="📝 Lyrics Commands",
            value=lyrics_commands,
            inline=False
        )

        examples = """
        • `!play Shape of You`
        • `!play Blinding Lights bassboost`
        • `!lyrics Shape of You - Ed Sheeran`
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
            search_term = query.strip()
            search_term = re.sub(r'\s+', '+', search_term)

            # Build URL with proper parameters
            url = f"{self.search_url}?q={search_term}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=10) as response:
                    if response.status != 200:
                        self.logger.error(f"AZLyrics API error: {response.status}")
                        return None

                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')

                    # Search for song results
                    results = soup.find_all('td', class_='text-left visitedlyr')

                    if not results:
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

                    return {
                        'title': title,
                        'artist': artist,
                        'url': url,
                        'source': 'AZLyrics',
                        'query': query
                    }

        except Exception as e:
            self.logger.error(f"Error in song search: {str(e)}")
            return None

    @commands.command(name='lyrics')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def lyrics(self, ctx, *, query: str):
        """Get lyrics for a song"""
        loading_msg = await ctx.send("🔍 Searching for lyrics...")

        try:
            result = await self.search_song_info(query)

            if not result:
                await loading_msg.edit(content=(
                    "❌ No lyrics found. Please try:\n"
                    "• Using the format: song - artist\n"
                    "• Checking spelling\n"
                    "• Using the full song title"
                ))
                return

            embed = discord.Embed(
                title=f"🎵 {result['title']}",
                color=discord.Color.blue()
            )
            embed.add_field(name="Artist", value=result['artist'], inline=False)
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


async def setup(bot):
    await bot.add_cog(MusicCommands(bot))