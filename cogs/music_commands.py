import discord
from discord.ext import commands
import logging
import yt_dlp
import asyncio
from typing import Dict, Optional

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

    @commands.command(name='play')
    async def play(self, ctx, *, url: str):
        """Play audio from a YouTube URL"""
        if not ctx.voice_client:
            # Try to join the user's channel if not already in one
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

        async with ctx.typing():
            try:
                with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                    self.logger.info(f"Attempting to extract info for URL: {url}")
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

async def setup(bot):
    await bot.add_cog(MusicCommands(bot))