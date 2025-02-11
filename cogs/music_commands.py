import discord
from discord.ext import commands
import logging
import yt_dlp
import asyncio
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from typing import Dict, Optional
import os

class MusicCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger('discord_bot')

        # Configure Spotify client if credentials are available
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

        # YouTube DL options
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

        # FFmpeg options
        self.ffmpeg_options = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn'
        }

    def get_spotify_track(self, spotify_url: str) -> Optional[str]:
        """Extract track information from Spotify URL"""
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

    async def get_youtube_audio(self, query: str) -> Optional[str]:
        """Search YouTube for audio URL"""
        try:
            ydl_opts = {
                'format': 'bestaudio/best',
                'noplaylist': True,
                'nocheckcertificate': True,
                'ignoreerrors': False,
                'quiet': True,
                'no_warnings': True,
                'source_address': '0.0.0.0'
            }

            loop = asyncio.get_event_loop()
            async with self.bot.loop.run_in_executor(None, lambda: yt_dlp.YoutubeDL(ydl_opts)) as ydl:
                info = await loop.run_in_executor(
                    None, 
                    lambda: ydl.extract_info(f"ytsearch:{query}", download=False)
                )
                if "entries" in info and len(info["entries"]) > 0:
                    return info["entries"][0]["url"]
            return None
        except Exception as e:
            self.logger.error(f"Error searching YouTube: {e}")
            return None

    @commands.command(name='join')
    async def join(self, ctx):
        """Join the user's voice channel"""
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

    @commands.command(name='play')
    async def play(self, ctx, *, query: str):
        """Play audio from a song name, YouTube URL, or Spotify URL"""
        if not ctx.author.voice:
            await ctx.send("❌ You must be in a voice channel!")
            return

        # Connect to voice if not already connected
        if not ctx.voice_client:
            try:
                await ctx.author.voice.channel.connect()
            except Exception as e:
                self.logger.error(f"Error connecting to voice: {e}")
                await ctx.send("❌ Could not join your voice channel!")
                return

        # Stop current playback if any
        if ctx.voice_client.is_playing():
            ctx.voice_client.stop()

        async with ctx.typing():
            try:
                # Handle Spotify URLs
                if "spotify.com/track/" in query:
                    query = self.get_spotify_track(query)
                    if not query:
                        await ctx.send("❌ Invalid Spotify URL or song not found.")
                        return

                # Search for song on YouTube (now properly async)
                youtube_url = await self.get_youtube_audio(query)
                if not youtube_url:
                    await ctx.send(f"❌ No songs found matching '{query}'!")
                    return

                # Create audio source and play
                source = await discord.FFmpegOpusAudio.from_probe(
                    youtube_url,
                    **self.ffmpeg_options
                )

                def after_playing(error):
                    if error:
                        self.logger.error(f"Player error: {error}")
                        asyncio.run_coroutine_threadsafe(
                            ctx.send("❌ An error occurred while playing the audio."),
                            self.bot.loop
                        )

                ctx.voice_client.play(source, after=after_playing)
                await ctx.send(f"🎵 Now playing: **{query}**")
                self.logger.info(f"Started playing: {query}")

            except Exception as e:
                self.logger.error(f"Error playing audio: {e}")
                await ctx.send("❌ An error occurred while trying to play the audio.")

    @commands.command(name='pause')
    async def pause(self, ctx):
        """Pause the currently playing audio"""
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.pause()
            await ctx.send("⏸️ Music paused.")
        else:
            await ctx.send("❌ No music is playing.")

    @commands.command(name='resume')
    async def resume(self, ctx):
        """Resume the paused audio"""
        if ctx.voice_client and ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            await ctx.send("▶️ Music resumed.")
        else:
            await ctx.send("❌ Music is not paused.")

    @commands.command(name='stop')
    async def stop(self, ctx):
        """Stop the currently playing audio"""
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send("⏹️ Music stopped.")
        else:
            await ctx.send("❌ No music is playing.")

async def setup(bot):
    await bot.add_cog(MusicCommands(bot))