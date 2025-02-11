import discord
from discord.ext import commands
import logging
import yt_dlp
import asyncio
from typing import Dict, Optional

class SongSelectView(discord.ui.View):
    def __init__(self, songs, timeout=30):
        super().__init__(timeout=timeout)
        self.selected_url = None

        # Create the select menu with song options
        options = []
        for song in songs[:25]:  # Discord limits to 25 options
            options.append(discord.SelectOption(
                label=song['title'][:100],  # Discord limits label to 100 chars
                description=f"Duration: {song['duration_string']} • Channel: {song['channel']}",
                value=song['url']
            ))

        select_menu = discord.ui.Select(
            placeholder="Choose a song to play...",
            options=options
        )

        async def select_callback(interaction: discord.Interaction):
            self.selected_url = select_menu.values[0]
            await interaction.response.send_message("🎵 Loading your selected song...", ephemeral=True)
            self.stop()

        select_menu.callback = select_callback
        self.add_item(select_menu)

class MusicCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger('discord_bot')
        self.voice_states = {}
        self.ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'nocheckcertificate': True,
            'ignoreerrors': False,
            'logtostderr': False,
            'quiet': True,
            'no_warnings': True,
            'source_address': '0.0.0.0',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        self.ffmpeg_options = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn'
        }

    async def search_songs(self, query: str) -> list:
        """Search for songs on YouTube"""
        search_opts = {
            **self.ydl_opts,
            'default_search': 'ytsearch5',  # Get top 5 results
            'extract_flat': True,
            'quiet': True,
            'no_warnings': True,
            'extract_flat': 'in_playlist'
        }

        try:
            with yt_dlp.YoutubeDL(search_opts) as ydl:
                self.logger.info(f"Searching for: {query}")
                results = await self.bot.loop.run_in_executor(
                    None, 
                    lambda: ydl.extract_info(f"ytsearch5:{query}", download=False)
                )

                if not results:
                    self.logger.error("No results found")
                    return []

                if 'entries' not in results:
                    self.logger.error("No entries in results")
                    return []

                songs = []
                for entry in results['entries']:
                    if not entry:
                        continue

                    duration_secs = entry.get('duration', 0)
                    minutes = duration_secs // 60 if duration_secs else 0
                    seconds = duration_secs % 60 if duration_secs else 0

                    # Use video ID to construct proper URL
                    video_id = entry.get('id', '')
                    url = f"https://www.youtube.com/watch?v={video_id}" if video_id else None

                    if not url:
                        continue

                    songs.append({
                        'title': entry.get('title', 'Unknown Title'),
                        'url': url,
                        'duration_string': f"{minutes}:{seconds:02d}",
                        'channel': entry.get('uploader', 'Unknown Channel')
                    })

                self.logger.info(f"Found {len(songs)} songs")
                return songs

        except Exception as e:
            self.logger.error(f"Error searching songs: {str(e)}")
            return []

    @commands.command(name='join')
    async def join(self, ctx):
        """Join the user's voice channel"""
        if not ctx.author.voice:
            await ctx.send("❌ You need to be in a voice channel first!")
            return

        channel = ctx.author.voice.channel
        if not channel.permissions_for(ctx.guild.me).connect:
            await ctx.send("❌ I don't have permission to join that channel!")
            return

        try:
            await channel.connect()
            await ctx.send(f"✅ Joined {channel.name}!")
            self.logger.info(f"Bot joined voice channel: {channel.name}")
        except Exception as e:
            self.logger.error(f"Error joining voice channel: {e}")
            await ctx.send("❌ An error occurred while joining the voice channel.")

    @commands.command(name='leave')
    async def leave(self, ctx):
        """Leave the current voice channel"""
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

    async def play_song(self, ctx, url: str):
        """Helper function to play a song from URL"""
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                self.logger.info(f"Extracting info for URL: {url}")
                info = await self.bot.loop.run_in_executor(None, lambda: ydl.extract_info(url, download=False))
                if not info:
                    await ctx.send("❌ Could not find the video!")
                    return

                url2 = info['url']
                self.logger.info(f"Creating FFmpeg audio source with URL: {url2}")
                source = await discord.FFmpegOpusAudio.from_probe(url2, **self.ffmpeg_options)

                def after_playing(error):
                    if error:
                        self.logger.error(f"Error after playing: {error}")
                        asyncio.run_coroutine_threadsafe(
                            ctx.send("❌ An error occurred while playing the audio."),
                            self.bot.loop
                        )

                ctx.voice_client.play(source, after=after_playing)
                await ctx.send(f"🎵 Now playing: **{info['title']}**")
                self.logger.info(f"Started playing: {info['title']}")

        except Exception as e:
            self.logger.error(f"Error playing audio: {e}")
            await ctx.send("❌ An error occurred while trying to play the audio.")

    @commands.command(name='play')
    async def play(self, ctx, *, query: str):
        """Play audio from a song name or YouTube URL"""
        if not ctx.voice_client:
            if ctx.author.voice:
                try:
                    await ctx.author.voice.channel.connect()
                except Exception as e:
                    self.logger.error(f"Error joining voice channel: {e}")
                    await ctx.send("❌ Could not join your voice channel!")
                    return
            else:
                await ctx.send("❌ You need to be in a voice channel first!")
                return

        # Stop current playback if any
        if ctx.voice_client.is_playing():
            ctx.voice_client.stop()

        # Check if it's a URL
        if 'youtube.com' in query or 'youtu.be' in query:
            await self.play_song(ctx, query)
            return

        # Search for the song
        async with ctx.typing():
            songs = await self.search_songs(query)
            if not songs:
                await ctx.send("❌ No songs found matching your search!")
                return

            # Create and send the selection menu
            view = SongSelectView(songs)
            message = await ctx.send(
                "🔍 I found these songs matching your search:",
                view=view
            )

            # Wait for selection
            await view.wait()
            await message.delete()

            if view.selected_url:
                await self.play_song(ctx, view.selected_url)
            else:
                await ctx.send("❌ No song was selected or the menu timed out.")

async def setup(bot):
    await bot.add_cog(MusicCommands(bot))