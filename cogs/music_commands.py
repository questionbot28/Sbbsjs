import discord
from discord.ext import commands
from discord import PCMVolumeTransformer
import logging
import asyncio
import aiohttp
import yt_dlp
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from typing import Dict, Optional, Any
import os
from discord.ui import View, Select, Button
from discord import ButtonStyle
import random
from discord.ext.commands import cooldown, BucketType
from datetime import datetime, timedelta
import time
import trafilatura
import json

class MusicCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger('discord_bot')
        self.youtube_together_id = "880218394199220334"
        self.current_volume = 1.0
        self.current_song_url = None
        self.retry_count = 0
        self.rate_limit_start = None
        self.rate_limit_resets = {}
        self.command_timestamps = {}
        self.max_retries = 5
        self.queue = []  # Add queue list for storing songs
        self.logger.info("MusicCommands cog initialized")

        # Initialize required clients
        self._initialize_clients()

    def _initialize_clients(self):
        """Initialize Genius and Spotify clients with proper error handling"""
        # Initialize YouTube-DL options
        self.ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'nocheckcertificate': True,
            'ignoreerrors': False,
            'quiet': True,
            'no_warnings': True,
            'source_address': '0.0.0.0',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'opus',
                'preferredquality': '192'
            }]
        }

        # Initialize Genius API client
        self.genius_token = os.getenv('GENIUS_API_KEY')
        if not self.genius_token:
            self.logger.warning("Genius API key not found. Lyrics feature will be disabled.")

        # Initialize Spotify client
        spotify_client_id = os.getenv('SPOTIFY_CLIENT_ID')
        spotify_client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
        if spotify_client_id and spotify_client_secret:
            try:
                self.sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
                    client_id=spotify_client_id,
                    client_secret=spotify_client_secret
                ))
                self.logger.info("Spotify client initialized successfully")
            except Exception as e:
                self.logger.error(f"Failed to initialize Spotify client: {e}")
                self.sp = None
        else:
            self.sp = None
            self.logger.warning("Spotify credentials not found. Spotify features will be disabled.")

    async def _ensure_voice_client(self, ctx):
        """Ensure bot is connected to voice channel"""
        if not ctx.voice_client:
            if not ctx.author.voice:
                await ctx.send("❌ You must be in a voice channel!")
                return False
            try:
                self.logger.info(f"Attempting to join voice channel: {ctx.author.voice.channel}")
                await ctx.author.voice.channel.connect()
                self.logger.info("Successfully joined voice channel")
                return True
            except Exception as e:
                self.logger.error(f"Error joining voice channel: {e}")
                await ctx.send("❌ Could not join your voice channel!")
                return False
        return True

    @commands.command(name='play')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def play(self, ctx, *, query: str):
        """Play a song in your voice channel with smooth progress updates"""
        self.logger.info(f"Play command invoked by {ctx.author} with query: {query}")

        try:
            if not await self._ensure_voice_client(ctx):
                return

            # Create initial searching embed
            embed = discord.Embed(
                title="🔍 Searching...",
                description=f"Looking for: **{query}**\nProgress: 0%",
                color=discord.Color.blue()
            )
            status_msg = await ctx.send(embed=embed)

            # Simulate gradual search progress
            for progress in range(0, 101, 5):
                embed.description = f"Looking for: **{query}**\nProgress: {progress}%"
                await status_msg.edit(embed=embed)
                await asyncio.sleep(0.2)  # Short delay between updates

            try:
                # Get YouTube results with enhanced metadata
                songs = []
                with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                    info = ydl.extract_info(f"ytsearch5:{query}", download=False)
                    if not info or 'entries' not in info:
                        embed.title = "❌ No Songs Found!"
                        embed.description = f"Could not find any songs matching '{query}'"
                        embed.color = discord.Color.red()
                        await status_msg.edit(embed=embed)
                        return

                    for entry in info["entries"][:5]:
                        song_info = {
                            "title": entry["title"],
                            "url": entry["url"],
                            "artist": entry.get("artist", entry.get("uploader", "Unknown Artist")),
                            "thumbnail": entry.get("thumbnail"),
                            "duration_ms": int(float(entry["duration"]) * 1000),  # Convert to milliseconds
                            "requester": ctx.author
                        }
                        songs.append(song_info)

                if not songs:
                    embed.title = "❌ No Songs Found!"
                    embed.description = f"Could not find any songs matching '{query}'"
                    embed.color = discord.Color.red()
                    await status_msg.edit(embed=embed)
                    return

                # Create song selection embed
                embed = discord.Embed(
                    title="🎵 Choose Your Song",
                    description="Select a song to play from the dropdown menu below:",
                    color=discord.Color.blue()
                )

                if songs[0].get('thumbnail'):
                    embed.set_thumbnail(url=songs[0]['thumbnail'])

                # Create and send view with song selection dropdown
                view = SongSelectionView(self.bot, ctx, songs)
                view.message = await status_msg.edit(embed=embed, view=view)

            except Exception as e:
                self.logger.error(f"Error in play command: {e}")
                embed.title = "❌ Error"
                embed.description = "An error occurred while processing your request."
                embed.color = discord.Color.red()
                await status_msg.edit(embed=embed)

        except commands.CommandOnCooldown as e:
            await ctx.send(f"⏳ Please wait {e.retry_after:.1f}s before using this command again.")
        except Exception as e:
            self.logger.error(f"Error in play command: {e}")
            await ctx.send(f"❌ An error occurred: {str(e)}")

    async def update_song_progress(self, voice_client, message, start_time, duration_ms, song_info):
        """Updates the song progress embed in real-time"""
        try:
            while voice_client and voice_client.is_connected() and voice_client.is_playing():
                # Calculate elapsed time and progress
                elapsed_ms = int((time.time() - start_time) * 1000)
                if elapsed_ms >= duration_ms:
                    return

                # Calculate progress percentage and bar
                progress_percent = min(100, (elapsed_ms / duration_ms) * 100)
                bar_length = 20
                filled_length = int(bar_length * progress_percent / 100)
                bar = '▰' * filled_length + '▱' * (bar_length - filled_length)

                # Format times for display
                elapsed = f"{int(elapsed_ms/60000):02d}:{int((elapsed_ms/1000)%60):02d}"
                total = f"{int(duration_ms/60000):02d}:{int((duration_ms/1000)%60):02d}"

                # Create progress embed
                embed = discord.Embed(
                    title=f"🎵 Now Playing: {song_info['title']}",
                    description=f"Artist: **{song_info['artist']}**\n\n"
                                f"Progress: `{bar}` **{progress_percent:.1f}%**\n"
                                f"Time: `{elapsed} / {total}`",
                    color=discord.Color.blue()
                )

                if song_info.get('thumbnail'):
                    embed.set_thumbnail(url=song_info['thumbnail'])

                embed.add_field(name="Duration", value=f"`{total}`", inline=True)
                embed.add_field(name="Requested by", value=song_info['requester'].mention, inline=True)

                # Update message with new progress
                try:
                    await message.edit(embed=embed)
                except discord.errors.HTTPException as e:
                    self.logger.error(f"Error updating progress message: {e}")
                    return

                # Wait before next update (2 seconds to reduce API calls)
                await asyncio.sleep(2)

        except Exception as e:
            self.logger.error(f"Error updating song progress: {e}")

    @commands.command(name='join')
    async def join(self, ctx):
        if not ctx.author.voice:
            await ctx.send("❌ You must be in a voice channel!")
            return

        try:
            channel = ctx.author.voice.channel
            if ctx.voice_client:
                if ctx.voice_client.channel.id == channel.id:
                    await ctx.send("✅ Already in your voice channel!")
                    return
                await ctx.voice_client.move_to(channel)
            else:
                await channel.connect()
            await ctx.send(f"✅ Joined {channel.name}!")
            self.logger.info(f"Bot joined voice channel: {channel.name}")
        except Exception as e:
            self.logger.error(f"Error joining voice channel: {e}")
            await ctx.send("❌ An error occurred while joining the voice channel.")

    @commands.command(name='leave')
    async def leave(self, ctx):
        if not ctx.voice_client:
            await ctx.send("❌ I'm not in a voice channel!")
            return

        try:
            await ctx.voice_client.disconnect()
            await ctx.send("👋 Left the voice channel!")
            self.logger.info("Bot left voice channel")
        except Exception as e:
            self.logger.error(f"Error leaving voice channel: {e}")
            await ctx.send("❌ An error occurred while leaving the voice channel.")

    @commands.command(name='pause')
    async def pause(self, ctx):
        if not ctx.voice_client:
            await ctx.send("❌ I'm not in a voice channel!")
            return

        if not ctx.voice_client.is_playing() and not ctx.voice_client.is_paused():
            await ctx.send("❌ No music is currently playing!")
            return

        if ctx.voice_client.is_paused():
            await ctx.send("❌ Music is already paused! Use `!resume` to continue playing.")
            return

        ctx.voice_client.pause()
        embed = discord.Embed(
            title="⏸️ Music Paused",
            description="Use `!resume` to continue playing.",
            color=discord.Color.yellow()
        )
        await ctx.send(embed=embed)

    @commands.command(name='resume')
    async def resume(self, ctx):
        if not ctx.voice_client:
            await ctx.send("❌ I'm not in a voice channel!")
            return

        if not ctx.voice_client.is_paused():
            if ctx.voice_client.is_playing():
                await ctx.send("❌ Music is already playing!")
            else:
                await ctx.send("❌ No music is currently paused!")
            return

        ctx.voice_client.resume()
        embed = discord.Embed(
            title="▶️ Music Resumed",
            description="Enjoy your music!",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

    @commands.command(name='stop')
    async def stop(self, ctx):
        if not ctx.voice_client:
            await ctx.send("❌ I'm not in a voice channel!")
            return

        if not ctx.voice_client.is_playing() and not ctx.voice_client.is_paused():
            await ctx.send("❌ No music is currently playing!")
            return

        try:
            # Stop the audio first
            ctx.voice_client.stop()
            # Reset the current song URL
            self.current_song_url = None
            # Reset volume to default
            self.current_volume = 1.0

            embed = discord.Embed(
                title="⏹️ Music Stopped",
                description="All playback has been stopped and settings reset.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
        except Exception as e:
            self.logger.error(f"Error stopping music: {e}")
            await ctx.send("❌ An error occurred while stopping the music.")

    @commands.command(name='vplay')
    async def vplay(self, ctx, *, query: str = ""):  # Changed from None to empty string
        try:
            if not ctx.author.voice:
                await ctx.send("❌ You must be in a voice channel!")
                return

            if not query:  # Changed condition to check empty string
                await ctx.send("❌ Please provide a song name!")
                return

            # Log permission check
            permissions = ctx.guild.me.guild_permissions
            required_perms = ['create_instant_invite', 'connect', 'speak']
            missing_perms = [perm for perm in required_perms if not getattr(permissions, perm)]

            if missing_perms:
                await ctx.send(f"❌ Missing required permissions: {', '.join(missing_perms)}")
                return

            # Initialize status_msg at the start
            status_msg = await ctx.send("🔍 Searching for your song...")

            try:
                video_url = self.get_youtube_video_url(query)
                if not video_url:
                    await status_msg.edit(content=f"❌ No videos found for '{query}'!")
                    return

                voice_channel_id = ctx.author.voice.channel.id

                async with aiohttp.ClientSession() as session:
                    json_data = {
                        "max_age": 86400,
                        "max_uses": 0,
                        "target_application_id": self.youtube_together_id,
                        "target_type": 2,
                        "temporary": False,
                        "validate": None,
                    }

                    self.logger.info(f"Creating Watch Party for: {query}")
                    await status_msg.edit(content="⚡ Creating Watch Party...")

                    async with session.post(
                        f"https://discord.com/api/v9/channels/{voice_channel_id}/invites",
                        json=json_data,
                        headers={"Authorization": f"Bot {self.bot.http.token}", "Content-Type": "application/json"}
                    ) as resp:
                        data = await resp.json()
                        self.logger.info(f"Watch Party created: {data}")

                        if resp.status != 200:
                            await status_msg.edit(content=f"❌ API Error: Status {resp.status}, Response: {data}")
                            return

                        if "code" not in data:
                            error_msg = data.get('message', 'Unknown error')
                            await status_msg.edit(content=f"❌ Failed to create Watch Party: {error_msg}")
                            return

                        invite_link = f"https://discord.com/invite/{data['code']}?video={video_url.split('v=')[-1]}"

                        embed = discord.Embed(
                            title="📽️ YouTube Watch Party Started!",
                            description=f"**Playing:** {query}",
                            color=0x00ff00
                        )
                        embed.add_field(
                            name="🎬 Join Watch Party",
                            value=f"[Click to Join]({invite_link})",
                            inline=False
                        )
                        embed.add_field(
                            name="🔊 Important: Enable Sound",
                            value="1. Join the Watch Party\n2. Click on the video\n3. Click the speaker icon (bottom-left) to unmute",
                            inline=False
                        )
                        embed.add_field(
                            name="▶️ Auto-Play Video",
                            value=f"[Click to Auto-Play](https://www.youtube.com/watch?v={video_url.split('v=')[-1]}&autoplay=1)",
                            inline=False
                        )
                        embed.set_footer(text="💡 Remember to unmute the video for sound!")

                        await status_msg.edit(content=None, embed=embed)
                        self.logger.info(f"Watch Party ready for: {query}")

            except Exception as e:
                self.logger.error(f"Error in watch party creation: {e}")
                if status_msg:
                    await status_msg.edit(content=f"❌ Error creating Watch Party: `{str(e)}`")
                else:
                    await ctx.send(f"❌ Error creating Watch Party: `{str(e)}`")

        except Exception as e:
            self.logger.error(f"Error in vplay command: {e}")
            await ctx.send(f"❌ Error creating Watch Party: `{str(e)}`")

    def get_youtube_video_url(self, query: str) -> Optional[str]:
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(f"ytsearch:{query}", download=False)
                if "entries" in info and len(info["entries"]) > 0:
                    return info["entries"][0]["webpage_url"]
                return None
        except Exception as e:
            self.logger.error(f"Error searching YouTube video: {e}")
            return None

    @commands.command(name='function')
    async def function(self, ctx):
        embed = discord.Embed(
            title="🎵 EduSphere Bot Music Features",
            description="Here are all the advanced commands your bot supports:",
            color=discord.Color.blue()
        )

        embed.add_field(name="🎶 Basic Commands", value="""
        `!play <song>` - Play a song from YouTube  
        `!pause` - Pause the current song  
        `!resume` - Resume the paused song  
        `!stop` - Stop playing music  
        `!leave` - Disconnect the bot from the voice channel  
        """, inline=False)

        embed.add_field(name="🔥 Advanced Music Effects", value="""
        `!play <song> bassboost` - Play song with **Bass Boost**  
        `!play <song> nightcore` - Play song with **Nightcore Effect**  
        `!play <song> reverb` - Play song with **Slow + Reverb Effect**  
        `!play <song> 8d` - Play song with **8D Surround Sound**  
        """, inline=False)

        embed.add_field(name="🎬 YouTube Watch Party", value="""
        `!vplay <song>` - Start a **YouTube Watch Party** and load the song automatically  
        """, inline=False)

        embed.add_field(name="🔧 Utility Commands", value="""
        `!join` - Make the bot join your voice channel  
        `!function` - Show all available bot commands
        `!volume <0-100>` - Set volume level
        `!seek forward/back` - Skip 10 seconds forward or backward
        `!lyrics <song>` - Get song lyrics
        `!queue` - View the music queue
        """, inline=False)

        embed.set_footer(text="🎵 EduSphere Bot - Your Ultimate Music Experience 🚀")

        await ctx.send(embed=embed)

    @commands.command(name='volume')
    @commands.cooldown(1, 2, BucketType.user)  # 1 command per 2 seconds per user
    async def volume(self, ctx, level: int):
        try:
            if not ctx.voice_client:
                await ctx.send("❌ The bot is not connected to a voice channel!")
                return

            if not ctx.voice_client.is_playing() and not ctx.voice_client.is_paused():
                await ctx.send("❌ No music is currently playing or paused!")
                return

            if level < 0 or level > 100:
                await ctx.send("❌ Please set volume between `0` and `100`!")
                return

            self.current_volume = level / 100  # Convert 0-100 scale to FFmpeg volume

            # Update volume of currently playing audio
            if isinstance(ctx.voice_client.source, PCMVolumeTransformer):
                ctx.voice_client.source.volume = self.current_volume
                # Create a visual representation of the volume level
                volume_bar = "▮" * (level // 10) + "▯" * ((100 - level) // 10)
                embed = discord.Embed(
                    title="🔊 Volume Adjusted",
                    description=f"**Volume:** `{level}%`\n`{volume_bar}`",
                    color=discord.Color.orange()
                )
                await ctx.send(embed=embed)
            else:
                await ctx.send("❌ Cannot adjust volume - incompatible audio source!")

        except commands.CommandOnCooldown as e:
            await ctx.send(f"⏳ Please wait {e.retry_after:.1f}s before adjusting volume again.")
            return
        except Exception as e:
            self.logger.error(f"Error adjusting volume: {e}")
            await ctx.send(f"❌ An error occurred while adjusting volume: {str(e)}")


    @commands.command(name='seek')
    async def seek(self, ctx, direction: str):
        if not ctx.voice_client or not ctx.voice_client.is_playing():
            await ctx.send("❌ The bot is not playing any music!")
            return

        if direction not in ["forward", "back"]:
            await ctx.send("❌ Use `!seek forward` or `!seek back`!")
            return

        if not self.current_song_url:
            await ctx.send("❌ No song is currently loaded!")
            return

        time_offset = 10 if direction == "forward" else -10
        vc = ctx.voice_client

        # Create animated embed for seeking
        embed = discord.Embed(
            title="⏭️ Seeking Song...",
            description=f"**{'Skipping forward' if direction == 'forward' else 'Rewinding'} by 10 seconds**",
            color=discord.Color.purple()
        )
        status_msg = await ctx.send(embed=embed)

        try:
            # Create new audio source with seek offset
            FFMPEG_OPTIONS = {
                "before_options": f"-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -probesize 100M -analyzeduration 100M -ss {abs(time_offset)}",
                "options": "-vn -b:a 256k -af volume=3.5,highpass=f=120,acompressor=threshold=-20dB:ratio=3:attack=0.2:release=0.3"
            }

            source = PCMVolumeTransformer(
                discord.FFmpegPCMAudio(self.current_song_url, **FFMPEG_OPTIONS),
                volume=self.current_volume
            )

            vc.stop()
            vc.play(source)

            # Update embed with success message
            embed.title = "✅ Seek Successful!"
            embed.description = f"{'⏩ Skipped' if direction == 'forward' else '⏪ Rewound'} **10 seconds** {'forward' if direction == 'forward' else 'backward'}"
            embed.color = discord.Color.green()
            await status_msg.edit(embed=embed)
        except Exception as e:
            self.logger.error(f"Error seeking: {e}")
            embed.title = "❌ Seek Failed"
            embed.description = f"An error occurred while seeking: {str(e)}"
            embed.color = discord.Color.red()
            await status_msg.edit(embed=embed)

    def _update_rate_limit(self, endpoint: str, reset_after: float):
        reset_time = datetime.now() + timedelta(seconds=reset_after)
        self.rate_limit_resets[endpoint] = reset_time
        if not self.rate_limit_start:
            self.rate_limit_start = datetime.now()

    def _should_retry(self, endpoint: str) -> bool:
        if self.retry_count >= self.max_retries:
            return False

        if endpoint in self.rate_limit_resets:
            if datetime.now() >= self.rate_limit_resets[endpoint]:
                del self.rate_limit_resets[endpoint]
                return True
        return len(self.rate_limit_resets) == 0

    @property
    def retry_delay(self) -> float:
        base_delay = 1.5
        max_delay = 60
        jitter = random.uniform(0, 0.5)  # Increased jitter for better distribution

        # Add progressive backoff based on global rate limit state
        if self.rate_limit_start:
            time_in_limit = (datetime.now() - self.rate_limit_start).total_seconds()
            additional_delay = min(time_in_limit / 10, 30)  # Cap at 30 seconds
        else:
            additional_delay = 0

        delay = min(base_delay * (2 ** self.retry_count) + additional_delay, max_delay) + jitter
        return delay

    async def handle_rate_limit(self, e, interaction=None, endpoint: str = "global"):
        try:
            # Extract rate limit information
            retry_after = getattr(e, 'retry_after', self.retry_delay)
            self._update_rate_limit(endpoint, retry_after)

            # Prepare user-friendly message
            if self.retry_count >= self.max_retries:
                message = "⚠️ Too many retries. Please try again in a few minutes."
                self.logger.warning(f"Rate limit max retries reached for {endpoint}")
                self.retry_count = 0  # Reset counter
                self.rate_limit_start = None
                return False

            delay = self.retry_delay
            warning_msg = (
                f"🕒 Rate limited! Retrying in {delay:.1f}s...\n"
                f"Retry {self.retry_count + 1}/{self.max_retries}"
            )

            # Log the rate limit
            self.logger.warning(
                f"Rate limit hit: endpoint={endpoint}, "
                f"retry={self.retry_count + 1}/{self.max_retries}, "
                f"delay={delay:.1f}s"
            )

            # Send feedback to user
            if interaction:
                try:
                    if isinstance(interaction, discord.Interaction):
                        if not interaction.response.is_done():
                            await interaction.response.defer(ephemeral=True)
                        await interaction.followup.send(warning_msg, ephemeral=True)
                    else:
                        # Assume it's a Context or Message
                        await interaction.edit(content=warning_msg)
                except discord.errors.HTTPException:
                    # If we can't send/edit message, log and continue
                    self.logger.warning("Could not send rate limit message to user")
                    pass

            # Wait with backoff
            await asyncio.sleep(delay)
            self.retry_count += 1

            # Check if we should continue retrying
            return self._should_retry(endpoint)

        except Exception as e:
            self.logger.error(f"Error in rate limit handler: {e}")
            return False

    async def lyrics(self, ctx, *, song_name: str):
        """Get lyrics for a song"""
        try:
            # Initialize status message
            embed = discord.Embed(
                title="🔍 Searching for Lyrics",
                description=f"Searching for: **{song_name}**",
                color=discord.Color.blue()
            )
            status_msg = await ctx.send(embed=embed)

            # Check if Genius token exists
            if not self.genius_token:
                embed.title = "❌ Error"
                embed.description = "Lyrics feature is not available. Please contact the bot administrator."
                embed.color = discord.Color.red()
                await status_msg.edit(embed=embed)
                return

            try:
                # Search for lyrics
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        f"https://api.genius.com/search?q={song_name}",
                        headers={'Authorization': f'Bearer {self.genius_token}'}
                    ) as response:
                        if response.status != 200:
                            embed.title = "❌ Error"
                            embed.description = "Could not connect to lyrics service."
                            embed.color = discord.Color.red()
                            await status_msg.edit(embed=embed)
                            return

                        try:
                            data = await response.json()
                            hits = data.get('response', {}).get('hits', [])

                            if not hits:
                                embed.title = "❌ No Results"
                                embed.description = f"Could not find lyrics for '{song_name}'"
                                embed.color = discord.Color.red()
                                await status_msg.edit(embed=embed)
                                return

                            # Get first hit
                            song_url = hits[0]['result']['url']

                            # Extract lyrics using trafilatura
                            downloaded = await self.bot.loop.run_in_executor(
                                None, trafilatura.fetch_url, song_url
                            )

                            if downloaded:
                                lyrics = await self.bot.loop.run_in_executor(
                                    None, trafilatura.extract, downloaded
                                )

                                if lyrics:
                                    # Split lyrics into chunks of 4096 characters (Discord embed limit)
                                    chunks = [lyrics[i:i + 4096] for i in range(0, len(lyrics), 4096)]

                                    # Send first chunk in original embed
                                    embed.title = f"🎵 Lyrics for {song_name}"
                                    embed.description = chunks[0]
                                    embed.color = discord.Color.blue()
                                    await status_msg.edit(embed=embed)

                                    # Send additional chunks if any
                                    if len(chunks) > 1:
                                        for chunk in chunks[1:]:
                                            await ctx.send(
                                                embed=discord.Embed(
                                                    description=chunk,
                                                    color=discord.Color.blue()
                                                )
                                            )
                                else:
                                    embed.title = "❌ Error"
                                    embed.description = "Could not extract lyrics from the page."
                                    embed.color = discord.Color.red()
                                    await status_msg.edit(embed=embed)
                            else:
                                embed.title = "❌ Error"
                                embed.description = "Could not download lyrics page."
                                embed.color = discord.Color.red()
                                await status_msg.edit(embed=embed)

                        except json.JSONDecodeError:
                            embed.title = "❌ Error"
                            embed.description = "Could not decode lyrics data."
                            embed.color = discord.Color.red()
                            await status_msg.edit(embed=embed)

            except Exception as e:
                self.logger.error(f"Error fetching lyrics: {e}")
                embed.title = "❌ Error"
                embed.description = f"An error occurred while fetching lyrics: {str(e)}"
                embed.color = discord.Color.red()
                await status_msg.edit(embed=embed)

        except Exception as e:
            self.logger.error(f"Error in lyrics command: {e}")
            await ctx.send(f"❌ An error occurred while processing your request: {str(e)}")

    @commands.command(name='queue')
    async def view_queue(self, ctx):
        """Display the current music queue"""
        if not self.queue:
            embed = discord.Embed(
                title="🎵 Music Queue",
                description="The queue is currently empty!",
                color=discord.Color.blue()
            )
            await ctx.send(embed=embed)
            return

        embed = discord.Embed(
            title="🎵 Music Queue",
            description=f"Currently {len(self.queue)} songs in queue",
            color=discord.Color.blue()
        )

        for i, song in enumerate(self.queue, 1):
            duration = f"{int(song['duration_ms']/60000)}:{int((song['duration_ms']/1000)%60):02d}"
            embed.add_field(
                name=f"{i}. {song['title']}",
                value=f"By: {song['artist']}\nDuration: {duration}\nRequested by: {song['requester'].mention}",
                inline=False
            )            
        await ctx.send(embed=embed)

    async def _play_next(self, ctx):
        """Play the next song in queue"""
        if not self.queue:
            return

        try:
            # Get next song from queue
            song = self.queue.pop(0)

            if not ctx.guild.voice_client:
                # Get the voice channel of the user who requested the song
                member = ctx.author if hasattr(ctx, 'author') else ctx.user
                if not member or not member.voice:
                    await self._send_message(ctx, "❌ You must be in a voice channel!", ephemeral=True)
                    return

                try:
                    await member.voice.channel.connect()
                except Exception as e:
                    self.logger.error(f"Error connecting to voice channel: {e}")
                    await self._send_message(ctx, "❌ Failed to connect to voice channel!", ephemeral=True)
                    return

            # Create FFmpeg audio source with enhanced options
            FFMPEG_OPTIONS = {
                'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -probesize 100M -analyzeduration 100M',
                'options': '-vn -b:a 192k -af volume=1.0'
            }

            try:
                source = discord.PCMVolumeTransformer(
                    discord.FFmpegPCMAudio(song['url'], **FFMPEG_OPTIONS),
                    volume=self.current_volume
                )
            except Exception as e:
                self.logger.error(f"Error creating audio source: {e}")
                await self._send_message(ctx, "❌ Error creating audio source. Please try again.", ephemeral=True)
                return

            # Store current song URL for seeking
            self.current_song_url = song['url']

            # Create now playing embed
            embed = discord.Embed(
                title="🎵 Now Playing",
                description=f"**{song['title']}**\nBy: {song['artist']}",
                color=discord.Color.blue()
            )

            if song.get('thumbnail'):
                embed.set_thumbnail(url=song['thumbnail'])

            embed.add_field(
                name="Duration",
                value=f"{int(song['duration_ms']/60000)}:{int((song['duration_ms']/1000)%60):02d}",
                inline=True
            )
            embed.add_field(
                name="Requested by",
                value=song['requester'].mention,
                inline=True
            )

            # Send the embed
            message = await ctx.send(embed=embed)

            # Define after playing callback
            def after_playing(error):
                if error:
                    self.logger.error(f"Error in playback: {error}")
                # Schedule next song if queue is not empty
                if len(self.queue) > 0:
                    asyncio.create_task(self._play_next(ctx))

            # Start playback
            ctx.guild.voice_client.play(source, after=after_playing)

            # Start progress tracking
            asyncio.create_task(
                self.update_song_progress(
                    ctx.guild.voice_client,
                    message,
                    time.time(),
                    song['duration_ms'],
                    song
                )
            )

        except Exception as e:
            self.logger.error(f"Error in _play_next: {e}")
            await self._send_message(ctx, "❌ An error occurred while playing the song.", ephemeral=True)

    async def _send_message(self, ctx, content, ephemeral=False):
        """Helper method to handle both Context and Interaction message sending"""
        try:
            if hasattr(ctx, 'send'):  # Context object
                await ctx.send(content)
            elif hasattr(ctx, 'response') and not ctx.response.is_done():  # Interaction not responded
                await ctx.response.send_message(content, ephemeral=ephemeral)
            else:  # Interaction already responded
                await ctx.followup.send(content, ephemeral=ephemeral)
        except Exception as e:
            self.logger.error(f"Error sending message: {e}")

    async def _handle_song_end(self, error, ctx):
        if error:
            self.logger.error(f"Error during song playback: {error}")

        await self._play_next(ctx)

    @commands.command(name='ydl_opts')
    async def ydl_opts(self, ctx):
        await ctx.send(f"ydl_opts: {self.ydl_opts}")

    class SongSelectionView(discord.ui.View):
        def __init__(self, bot, ctx, songs):
            super().__init__(timeout=30)
            self.bot = bot
            self.ctx = ctx
            self.songs = songs
            self.message = None
            self.logger = logging.getLogger('discord_bot')

            # Create song selection dropdown
            options = []
            for i, song in enumerate(songs, 1):
                duration = f"{int(song['duration_ms']/60000)}:{int((song['duration_ms']/1000)%60):02d}"
                options.append(
                    discord.SelectOption(
                        label=f"{song['title'][:80]}",  # Discord has 100 char limit
                        description=f"By {song['artist'][:80]} • {duration}",
                        value=str(i-1)
                    )
                )

            # Add select menu to the view
            select_menu = discord.ui.Select(
                placeholder="Choose a song to play...",
                options=options
            )
            select_menu.callback = self.song_selected
            self.add_item(select_menu)

        async def song_selected(self, interaction: discord.Interaction):
            try:
                # Get selected song
                song_index = int(interaction.data['values'][0])
                selected_song = self.songs[song_index]

                # Add to queue
                music_cog = self.bot.get_cog('MusicCommands')
                if not music_cog:
                    await interaction.response.send_message("❌ Music system error", ephemeral=True)
                    return

                music_cog.queue.append(selected_song)

                # Update embed
                embed = discord.Embed(
                    title="✅ Song Added to Queue",
                    description=f"**{selected_song['title']}**\nBy: {selected_song['artist']}",
                    color=discord.Color.green()
                )

                if selected_song.get('thumbnail'):
                    embed.set_thumbnail(url=selected_song['thumbnail'])

                await interaction.response.edit_message(embed=embed, view=None)

                # Start playing if not already playing
                if not self.ctx.voice_client or not self.ctx.voice_client.is_playing():
                    await music_cog._play_next(self.ctx)

            except Exception as e:
                self.logger.error(f"Error in song selection: {e}")
                await interaction.response.send_message(
                    "❌ An error occurred while selecting the song.",
                    ephemeral=True
                )

        async def on_timeout(self):
            if self.message:
                await self.message.edit(view=None)

async def setup(bot):
    await bot.add_cog(MusicCommands(bot))