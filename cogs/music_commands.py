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
import re

class SongSelectionView(discord.ui.View):
    def __init__(self, bot, ctx, songs, effect=None):
        super().__init__(timeout=15)  # Reduced timeout
        self.ctx = ctx
        self.songs = songs
        self.bot = bot
        self.effect = effect
        self.message = None  # Store message reference

        select = discord.ui.Select(placeholder="Choose a song...", min_values=1, max_values=1)

        for i, song in enumerate(songs[:5]):  # Only show top 5 results
            title = song["title"][:100]
            select.add_option(label=title, value=str(i))

        select.callback = self.song_selected
        self.add_item(select)

    async def song_selected(self, interaction: discord.Interaction):
        try:
            await interaction.response.defer()  # Acknowledge interaction immediately
            bot_cog = self.bot.get_cog('MusicCommands')
            if not bot_cog:
                await interaction.followup.send("❌ Bot configuration error!", ephemeral=True)
                return

            selected_index = int(interaction.data["values"][0])
            song = self.songs[selected_index]

            # Add song to queue
            queue_entry = {
                'title': song['title'],
                'url': song['url'],
                'requester': interaction.user
            }
            bot_cog.queue.append(queue_entry)

            # If nothing is playing, start playing
            if not interaction.guild.voice_client or not interaction.guild.voice_client.is_playing():
                await bot_cog._play_next(interaction)
            else:
                await interaction.followup.send(f"🎵 Added to queue: **{song['title']}**")

        except Exception as e:
            self.logger.error(f"Error in song selection: {e}")
            await interaction.followup.send(f"❌ Error adding song to queue: {str(e)}", ephemeral=True)


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

        # Initialize Genius API client
        self.genius_token = os.getenv('GENIUS_API_KEY')
        if not self.genius_token:
            self.logger.warning("Genius API key not found. Lyrics feature will be disabled.")

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
                'preferredquality': '128'
            }]
        }

        # Configure Spotify if credentials exist
        spotify_client_id = os.getenv('SPOTIFY_CLIENT_ID')
        spotify_client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
        if spotify_client_id and spotify_client_secret:
            self.sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
                client_id=spotify_client_id,
                client_secret=spotify_client_secret
            ))
        else:
            self.sp = None
            self.logger.warning("Spotify credentials not found. Spotify features will be disabled.")

    async def get_youtube_results(self, query: str) -> Optional[list]:
        def search():
            try:
                with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                    info = ydl.extract_info(f"ytsearch5:{query}", download=False)
                    if not info or 'entries' not in info:
                        return None
                    return [
                        {"title": entry["title"], "url": entry["url"]}
                        for entry in info["entries"][:5]
                    ]
            except Exception as e:
                self.logger.error(f"Error searching YouTube: {e}")
                return None

        return await asyncio.get_event_loop().run_in_executor(None, search)

    def get_spotify_track(self, spotify_url: str) -> Optional[str]:
        if not self.sp:
            return None

        try:
            track = self.sp.track(spotify_url)
            song_name = track["name"]
            artist_name = track["artists"][0]["name"]
            return f"{song_name} by {artist_name}"
        except Exception as e:
            self.logger.error(f"Error getting Spotify track: {e}")
            return None


    @commands.command(name='play')
    @commands.cooldown(1, 5, BucketType.user)  # 1 command per 5 seconds per user
    async def play(self, ctx, *, query: str):
        try:
            if not ctx.author.voice:
                await ctx.send("❌ You must be in a voice channel!")
                return

            # Extract effect from query (last word)
            args = query.split()
            effect = args[-1].lower() if len(args) > 1 else None
            if effect not in ["bassboost", "nightcore", "reverb", "8d"]:
                effect = None
                song_query = query
            else:
                song_query = " ".join(args[:-1])

            # Create initial embed
            embed = discord.Embed(
                title="🎵 Searching for Song...",
                description=f"🔍 Finding **{song_query}** on YouTube...",
                color=discord.Color.blue()
            )
            status_msg = await ctx.send(embed=embed)
            self.logger.info(f"Searching for song: {song_query}")

            try:
                # Handle Spotify URLs
                if "spotify.com/track/" in song_query and self.sp:
                    song_query = self.get_spotify_track(song_query)
                    if not song_query:
                        embed.title = "❌ Invalid Spotify URL!"
                        embed.description = "Could not find the specified track."
                        embed.color = discord.Color.red()
                        await status_msg.edit(embed=embed)
                        return

                # Get YouTube results asynchronously
                songs = await self.get_youtube_results(song_query)
                if not songs:
                    embed.title = "❌ No Songs Found!"
                    embed.description = f"Could not find any songs matching '{song_query}'"
                    embed.color = discord.Color.red()
                    await status_msg.edit(embed=embed)
                    return

                # Show song selection dropdown with effect
                view = SongSelectionView(self.bot, ctx, songs, effect)
                effect_msg = f" with {effect} effect" if effect else ""
                embed.title = "🎵 Select a Song"
                embed.description = f"Choose a song to play{effect_msg}:"
                embed.color = discord.Color.green()
                await status_msg.edit(embed=embed, view=view)
                self.logger.info(f"Song options presented to user for query: {song_query}")

            except discord.errors.HTTPException as e:
                if e.status == 429:  # Rate limit error
                    await self.handle_rate_limit(e, status_msg, endpoint="play")
                else:
                    self.logger.error(f"HTTP error in play command: {e}")
                    embed.title = "❌ Discord API Error"
                    embed.description = "Please try again in a few moments."
                    embed.color = discord.Color.red()
                    await status_msg.edit(embed=embed)
            except Exception as e:
                self.logger.error(f"Error in play command: {e}")
                embed.title = "❌ Error Occurred"
                embed.description = f"An error occurred while searching: {str(e)}"
                embed.color = discord.Color.red()
                await status_msg.edit(embed=embed)

        except commands.CommandOnCooldown as e:
            await ctx.send(f"⏳ Please wait {e.retry_after:.1f}s before using this command again.")
            return
        except Exception as e:
            self.logger.error(f"Error in play command: {e}")
            await ctx.send(f"❌ An error occurred: {str(e)}")

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
    async def vplay(self, ctx, *, query: str = None):
        try:
            if not ctx.author.voice:
                await ctx.send("❌ You must be in a voice channel!")
                return

            if not query:
                await ctx.send("❌ Please provide a song name!")
                return

            # Log permission check
            permissions = ctx.guild.me.guild_permissions
            required_perms = ['create_instant_invite', 'connect', 'speak']
            missing_perms = [perm for perm in required_perms if not getattr(permissions, perm)]

            if missing_perms:
                await ctx.send(f"❌ Missing required permissions: {', '.join(missing_perms)}")
                return

            # Send searching message
            status_msg = await ctx.send("🔍 Searching for your song...")

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

    @commands.command(name='lyrics')
    async def lyrics(self, ctx, *, song_name: str):
        """Fetch lyrics for a song from Genius"""
        if not self.genius_token:
            await ctx.send("❌ Lyrics feature is not available - Genius API key not configured.")
            return

        try:
            # Send searching message with embed
            embed = discord.Embed(
                title="🔍 Searching for Lyrics",
                description=f"Searching for: **{song_name}**",
                color=discord.Color.blue()
            )
            status_msg = await ctx.send(embed=embed)

            # Search for the song using Genius API directly
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.genius_token}",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "Accept": "application/json"
                }
                search_url = f"https://api.genius.com/search?q={song_name}"

                self.logger.info(f"Searching Genius for: {song_name}")
                async with session.get(search_url, headers=headers) as response:
                    if response.status != 200:
                        error_msg = await response.text()
                        self.logger.error(f"Genius API error: {error_msg}")
                        embed.title = "❌ API Error"
                        embed.description = f"Failed to search for lyrics (Status: {response.status})"
                        embed.color = discord.Color.red()
                        await status_msg.edit(embed=embed)
                        return

                    data = await response.json()

                    if not data['response']['hits']:
                        embed.title = "❌ No Results"
                        embed.description = f"No lyrics found for: **{song_name}**"
                        embed.color = discord.Color.red()
                        await status_msg.edit(embed=embed)
                        return

                    # Get the first result
                    first_hit = data['response']['hits'][0]
                    song_title = first_hit['result']['title']
                    artist_name = first_hit['result']['primary_artist']['name']
                    song_url = first_hit['result']['url']

                    # Log the found song details
                    self.logger.info(f"Found song: {song_title} by {artist_name} at {song_url}")

                    # Update status message
                    embed.title = "📥 Found Song!"
                    embed.description = f"Fetching lyrics for **{song_title}** by **{artist_name}**"
                    embed.color = discord.Color.gold()
                    await status_msg.edit(embed=embed)

                    # Download and extract lyrics using trafilatura with improved settings
                    downloaded = await asyncio.get_event_loop().run_in_executor(
                        None,
                        lambda: trafilatura.fetch_url(
                            song_url,
                            config={
                                'USER_AGENT': headers['User-Agent'],
                                'TIMEOUT': 30,
                                'MAX_REDIRECTS': 5
                            }
                        )
                    )

                    if not downloaded:
                        self.logger.error(f"Failed to fetch lyrics page: {song_url}")
                        embed.title = "❌ Access Error"
                        embed.description = "Failed to access the lyrics page. The song might be restricted."
                        embed.color = discord.Color.red()
                        await status_msg.edit(embed=embed)
                        return

                    lyrics = await asyncio.get_event_loop().run_in_executor(
                        None,
                        lambda: trafilatura.extract(
                            downloaded,
                            include_comments=False,
                            include_tables=False,
                            no_fallback=False,
                            target_language='en'
                        )
                    )

                    if not lyrics:
                        self.logger.error(f"Failed to extract lyrics from page content")
                        embed.title = "❌ Extraction Error"
                        embed.description = "Could not extract lyrics from the page."
                        embed.color = discord.Color.red()
                        await status_msg.edit(embed=embed)
                        return

                    # Clean up lyrics with improved regex
                    lyrics = re.sub(r'\[.*?\]|\(.*?\)', '', lyrics)  # Remove [...] and (...) annotations
                    lyrics = re.sub(r'\n{3,}', '\n\n', lyrics)  # Normalize line breaks
                    lyrics = re.sub(r'\s+', ' ', lyrics)  # Normalize whitespace
                    lyrics = lyrics.strip()

                    # Split lyrics into chunks with smarter splitting
                    chunk_size = 4000
                    chunks = []
                    current_chunk = ""
                    
                    for line in lyrics.split('\n'):
                        if len(current_chunk) + len(line) + 1 > chunk_size:
                            chunks.append(current_chunk.strip())
                            current_chunk = line
                        else:
                            current_chunk += '\n' + line if current_chunk else line
                    
                    if current_chunk:
                        chunks.append(current_chunk.strip())

                    # Create rich embed for first chunk
                    first_embed = discord.Embed(
                        title=f"🎵 {song_title}",
                        description=chunks[0],
                        color=discord.Color.blue(),
                        url=song_url
                    )
                    first_embed.add_field(name="👤 Artist", value=artist_name, inline=True)
                    first_embed.add_field(name="📄 Pages", value=f"{len(chunks)}", inline=True)
                    first_embed.set_footer(text=f"Powered by Genius | Page 1 of {len(chunks)}")
                    await status_msg.edit(embed=first_embed)

                    # Send remaining chunks with consistent formatting
                    for i, chunk in enumerate(chunks[1:], 2):
                        embed = discord.Embed(
                            title=f"🎵 {song_title} (Continued)",
                            description=chunk,
                            color=discord.Color.blue(),
                            url=song_url
                        )
                        embed.set_footer(text=f"Page {i} of {len(chunks)}")
                        await ctx.send(embed=embed)

                    self.logger.info(f"Successfully fetched and displayed lyrics for: {song_title}")

        except aiohttp.ClientError as e:
            self.logger.error(f"Network error fetching lyrics: {e}")
            await status_msg.edit(content="❌ Network error while fetching lyrics. Please try again later.")
        except Exception as e:
            self.logger.error(f"Error fetching lyrics: {e}")
            await status_msg.edit(content=f"❌ An error occurred while fetching lyrics: {str(e)}")

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

        # Create queue embed
        embed = discord.Embed(
            title="🎶 Music Queue",
            color=discord.Color.blue()
        )

        # Add current song if playing
        if ctx.voice_client and ctx.voice_client.is_playing():
            embed.add_field(
                name="🎵 Now Playing",
                value=f"**{self.queue[0]['title']}**\nRequested by: {self.queue[0]['requester'].mention}",
                inline=False
            )

        # Add upcoming songs (up to 10)
        queue_start = 1 if ctx.voice_client and ctx.voice_client.is_playing() else 0
        for i, song in enumerate(self.queue[queue_start:10], start=1):
            embed.add_field(
                name=f"{i}. {song['title']}",
                value=f"Requested by: {song['requester'].mention}",
                inline=False
            )

        # Add total songs info
        remaining = len(self.queue) - 10 if len(self.queue) > 10 else 0
        if remaining > 0:
            embed.set_footer(text=f"And {remaining} more songs in queue")

        await ctx.send(embed=embed)

    async def _play_next(self, ctx):
        """Helper method to play the next song in queue"""
        if not self.queue:
            return

        vc = ctx.guild.voice_client
        if not vc:
            if ctx.author.voice:
                vc = await ctx.author.voice.channel.connect()
            else:
                await ctx.send("❌ You must be in a voice channel!")
                return

        # Get the first song in queue
        song = self.queue[0]

        # Apply audio effects if specified
        FFMPEG_OPTIONS = {
            "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -probesize 100M -analyzeduration 100M",
            "options": "-vn -b:a 256k -af volume=3.5,highpass=f=120,acompressor=threshold=-20dB:ratio=3:attack=0.2:release=0.3"
        }

        try:
            source = PCMVolumeTransformer(
                discord.FFmpegPCMAudio(song['url'], **FFMPEG_OPTIONS),
                volume=self.current_volume
            )

            def after_playing(error):
                if error:
                    self.logger.error(f"Error playing audio: {error}")

                # Remove the song that just finished
                if self.queue:
                    self.queue.pop(0)

                # Schedule playing the next song
                if self.queue:
                    coro = self._play_next(ctx)
                    fut = asyncio.run_coroutine_threadsafe(coro, self.bot.loop)
                    try:
                        fut.result()
                    except Exception as e:
                        self.logger.error(f"Error in after_playing: {e}")

            vc.play(source, after=after_playing)
            await ctx.send(f"🎶 Now playing: **{song['title']}**\nRequested by: {song['requester'].mention}")

        except Exception as e:
            self.logger.error(f"Error playing audio: {e}")
            await ctx.send(f"❌ Error playing audio: {str(e)}")
            if self.queue:
                self.queue.pop(0)
            await self._play_next(ctx)

async def setup(bot):
    await bot.add_cog(MusicCommands(bot))