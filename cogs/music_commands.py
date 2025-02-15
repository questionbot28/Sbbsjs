import discord
from discord.ext import commands
import asyncio
import random
import yt_dlp
import aiohttp
import xml.etree.ElementTree as ET
from async_timeout import timeout
from collections import deque
import os #added import for os.getenv
from server import update_now_playing

class MusicPlayer:
    def __init__(self, ctx):
        self.bot = ctx.bot
        self.guild = ctx.guild
        self.channel = ctx.channel
        self.cog = ctx.cog
        self.queue = deque()
        self.next = asyncio.Event()
        self.current = None
        self.volume = 0.5
        self.loop = False
        self.shuffle = False
        self.autoplay = False
        self.update_web_ui()

        ctx.bot.loop.create_task(self.player_loop())

    def update_web_ui(self):
        """Update web UI with current song information"""
        try:
            if self.current:
                song_info = {
                    "title": self.current['title'],
                    "artist": self.current['requester'].name,
                    "progress": 0,
                    "duration": self.current['duration'],
                    "thumbnail": self.current.get('thumbnail', "https://via.placeholder.com/150")
                }
                update_now_playing(song_info)
            else:
                update_now_playing({
                    "title": "No song playing",
                    "artist": "",
                    "progress": 0,
                    "duration": 100,
                    "thumbnail": "https://via.placeholder.com/150"
                })
        except Exception as e:
            self.bot.logger.error(f"Error updating web UI: {e}")

    async def player_loop(self):
        """Main player loop."""
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            self.next.clear()
            if self.loop and self.current:
                self.queue.append(self.current)
            elif not self.queue and self.autoplay and self.current:
                try:
                    related = await self.get_related_song(self.current['url'])
                    if related:
                        self.queue.append(related)
                except Exception as e:
                    self.bot.logger.error(f"Autoplay error: {e}")

            if self.shuffle and len(self.queue) > 1:
                queue_list = list(self.queue)
                random.shuffle(queue_list)
                self.queue = deque(queue_list)

            try:
                async with timeout(300):
                    self.current = await self.queue.popleft()
            except asyncio.TimeoutError:
                return self.bot.loop.create_task(self.stop())
            except IndexError:
                continue

            try:
                source = await discord.FFmpegOpusAudio.from_probe(
                    self.current['url'],
                    **{'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'}
                )
                self.guild.voice_client.play(source, after=lambda _: self.bot.loop.call_soon_threadsafe(self.next.set))
                await self.channel.send(f"🎵 Now playing: **{self.current['title']}**")
                self.update_web_ui()
                await self.next.wait()
            except Exception as e:
                self.bot.logger.error(f"Player error: {e}")
                continue

class MusicCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = bot.logger
        self.players = {}
        self.ytdl_opts = {
            'format': 'bestaudio/best',
            'extractaudio': True,
            'audioformat': 'mp3',
            'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
            'restrictfilenames': True,
            'noplaylist': True,
            'nocheckcertificate': True,
            'ignoreerrors': False,
            'logtostderr': False,
            'quiet': True,
            'no_warnings': True,
            'default_search': 'auto',
            'source_address': '0.0.0.0'
        }
        self.ytdl = yt_dlp.YoutubeDL(self.ytdl_opts)

    async def get_player(self, ctx):
        player = self.players.get(ctx.guild.id)
        if not player:
            player = MusicPlayer(ctx)
            self.players[ctx.guild.id] = player
        return player

    @commands.command(name='play')
    async def play(self, ctx, *, query: str):
        async with ctx.typing():
            try:
                if not ctx.voice_client:
                    if not ctx.author.voice:
                        return await ctx.send("❌ You're not connected to a voice channel!")
                    await ctx.author.voice.channel.connect()

                player = await self.get_player(ctx)
                data = await self.bot.loop.run_in_executor(None, lambda: self.ytdl.extract_info(query, download=False))

                if 'entries' in data:
                    data = data['entries'][0]

                song = {
                    'url': data['url'],
                    'title': data['title'],
                    'duration': data['duration'],
                    'requester': ctx.author
                }
                player.queue.append(song)
                await ctx.send(f"✅ Added to queue: **{data['title']}**")

            except Exception as e:
                self.logger.error(f"Play command error: {e}")
                await ctx.send(f"❌ An error occurred: {str(e)}")

    @commands.command(name='status')
    async def status(self, ctx):
        try:
            player = await self.get_player(ctx)
            status_embed = discord.Embed(
                title="🎵 Music Player Status",
                color=discord.Color.blue()
            )

            modes = [
                ("🔁 Loop Mode", player.loop),
                ("🔀 Shuffle Mode", player.shuffle),
                ("▶️ Autoplay", player.autoplay)
            ]

            status_text = "\n".join([f"{name}: {'✅ Enabled' if status else '❌ Disabled'}"
                                   for name, status in modes])

            status_embed.add_field(
                name="Active Modes",
                value=status_text,
                inline=False
            )

            if player.current:
                status_embed.add_field(
                    name="Now Playing",
                    value=f"🎵 {player.current['title']}",
                    inline=False
                )

            queue_length = len(player.queue)
            status_embed.add_field(
                name="Queue Status",
                value=f"📋 Songs in queue: {queue_length}",
                inline=False
            )

            await ctx.send(embed=status_embed)
        except Exception as e:
            self.logger.error(f"Error showing status: {e}")
            await ctx.send("❌ An error occurred while getting player status.")

    @commands.command(name='loop')
    async def loop(self, ctx):
        try:
            if not ctx.voice_client:
                return await ctx.send("❌ I'm not connected to a voice channel!")

            player = await self.get_player(ctx)
            player.loop = not player.loop
            mode = "enabled" if player.loop else "disabled"

            embed = discord.Embed(
                title="🔁 Loop Mode",
                description=f"Loop mode has been {mode}!",
                color=discord.Color.green() if player.loop else discord.Color.red()
            )

            if player.current:
                embed.add_field(
                    name="Current Track",
                    value=f"🎵 {player.current['title']}",
                    inline=False
                )

            await ctx.send(embed=embed)
        except Exception as e:
            self.logger.error(f"Loop command error: {e}")
            await ctx.send("❌ An error occurred while toggling loop mode.")

    @commands.command(name='shuffle')
    async def shuffle(self, ctx):
        try:
            if not ctx.voice_client:
                return await ctx.send("❌ I'm not connected to a voice channel!")

            player = await self.get_player(ctx)
            player.shuffle = not player.shuffle
            mode = "enabled" if player.shuffle else "disabled"

            embed = discord.Embed(
                title="🔀 Shuffle Mode",
                description=f"Shuffle mode has been {mode}!",
                color=discord.Color.green() if player.shuffle else discord.Color.red()
            )

            if len(player.queue) > 0:
                embed.add_field(
                    name="Queue Status",
                    value=f"📋 {len(player.queue)} songs in queue",
                    inline=False
                )

            await ctx.send(embed=embed)
        except Exception as e:
            self.logger.error(f"Shuffle command error: {e}")
            await ctx.send("❌ An error occurred while toggling shuffle mode.")

    @commands.command(name='autoplay')
    async def autoplay(self, ctx):
        try:
            if not ctx.voice_client:
                return await ctx.send("❌ I'm not connected to a voice channel!")

            player = await self.get_player(ctx)
            player.autoplay = not player.autoplay
            mode = "enabled" if player.autoplay else "disabled"

            embed = discord.Embed(
                title="▶️ Autoplay Mode",
                description=f"Autoplay has been {mode}!",
                color=discord.Color.green() if player.autoplay else discord.Color.red()
            )

            if player.autoplay:
                embed.add_field(
                    name="Info",
                    value="I'll automatically play related songs when the queue is empty!",
                    inline=False
                )

            await ctx.send(embed=embed)
        except Exception as e:
            self.logger.error(f"Autoplay command error: {e}")
            await ctx.send("❌ An error occurred while toggling autoplay mode.")

    @commands.command(name='queue')
    async def queue(self, ctx):
        player = await self.get_player(ctx)
        if not player.queue and not player.current:
            return await ctx.send("❌ Queue is empty!")

        embed = discord.Embed(title="🎵 Music Queue", color=discord.Color.blue())
        if player.current:
            embed.add_field(
                name="Now Playing",
                value=f"**{player.current['title']}** | Requested by {player.current['requester'].mention}",
                inline=False
            )

        queue_list = []
        for i, song in enumerate(player.queue, 1):
            queue_list.append(f"{i}. **{song['title']}** | Requested by {song['requester'].mention}")

        if queue_list:
            embed.add_field(
                name="Up Next",
                value="\n".join(queue_list[:10]) + "\n..." if len(queue_list) > 10 else "\n".join(queue_list),
                inline=False
            )

        embed.set_footer(text=f"Loop: {'✅' if player.loop else '❌'} | Shuffle: {'✅' if player.shuffle else '❌'} | Autoplay: {'✅' if player.autoplay else '❌'}")
        await ctx.send(embed=embed)

    @commands.command(name='skip')
    async def skip(self, ctx):
        if not ctx.voice_client or not ctx.voice_client.is_playing():
            return await ctx.send("❌ Nothing is playing!")
        ctx.voice_client.stop()
        await ctx.send("⏭️ Skipped the current song!")

    @commands.command(name='stop')
    async def stop(self, ctx):
        player = await self.get_player(ctx)
        player.queue.clear()
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
        self.players.pop(ctx.guild.id, None)
        await ctx.send("⏹️ Music playback stopped and queue cleared!")


    async def get_lyrics(self, song_name: str) -> str:
        encoded_query = song_name.replace(' ', '%20')
        url = f"http://api.chartlyrics.com/apiv1.asmx/SearchLyricText?lyricText={encoded_query}"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        self.logger.error(f"ChartLyrics API error: {response.status}")
                        return "❌ Lyrics service is currently unavailable. Please try again later."

                    data = await response.text()
                    self.logger.debug(f"ChartLyrics API response: {data}")

                    if not data or data.isspace():
                        return "❌ Empty response from lyrics service."

                    try:
                        root = ET.fromstring(data)
                        search_results = root.findall(".//SearchLyricResult")

                        if not search_results:
                            suggestion_msg = (
                                f"❌ No lyrics found for '{song_name}'. Try:\n"
                                "• Adding the artist name (e.g., '295 Sidhu Moose Wala')\n"
                                "• Using the full song title\n"
                                "• Checking for typos"
                            )
                            return suggestion_msg

                        first_result = search_results[0]

                        song_title = first_result.find("Song")
                        song_title = song_title.text if song_title is not None else "Unknown Title"

                        artist = first_result.find("Artist")
                        artist = artist.text if artist is not None else "Unknown Artist"

                        lyrics_url = first_result.find("LyricUrl")
                        if lyrics_url is None or not lyrics_url.text:
                            return "❌ No lyrics URL available for this song."

                        lyrics_url = lyrics_url.text

                        self.logger.info(f"Found lyrics for: {song_title} by {artist}")

                        return {
                            "title": song_title,
                            "artist": artist,
                            "url": lyrics_url,
                            "query": song_name
                        }

                    except ET.ParseError as e:
                        self.logger.error(f"XML parsing error: {e}")
                        self.logger.error(f"Raw XML data: {data[:200]}...")
                        return "❌ Error processing lyrics data. Try a different song name."

        except aiohttp.ClientError as e:
            self.logger.error(f"Network error while fetching lyrics: {e}")
            return "❌ Could not connect to lyrics service. Please try again later."
        except Exception as e:
            self.logger.error(f"Unexpected error fetching lyrics: {e}")
            return f"❌ An error occurred while fetching lyrics: {str(e)}"

    @commands.command(name='lyrics')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def lyrics(self, ctx, *, query: str):
        loading_msg = await ctx.send("🔍 Searching for lyrics...")

        try:
            self.logger.info(f"Searching lyrics for query: {query}")

            parts = query.split('-')
            if len(parts) == 2:
                song_title = parts[0].strip()
                artist = parts[1].strip()
                result = await self.get_lyrics(song_title)
            else:
                result = await self.get_lyrics(query)

            if isinstance(result, str):
                error_embed = discord.Embed(
                    title="Lyrics Search Result",
                    description=result,
                    color=discord.Color.red()
                )
                await loading_msg.edit(embed=error_embed)
                return

            embed = discord.Embed(
                title=f"🎵 {result['title']}",
                description=f"Search query: **{result['query']}**",
                color=discord.Color.blue()
            )

            embed.add_field(
                name="Artist",
                value=result['artist'],
                inline=False
            )

            embed.add_field(
                name="Lyrics Link",
                value=f"[Click here to view lyrics]({result['url']})",
                inline=False
            )

            embed.set_footer(text="Lyrics provided by ChartLyrics")
            await loading_msg.edit(embed=embed)

        except commands.CommandOnCooldown as e:
            await loading_msg.edit(content=f"⏳ Please wait {e.retry_after:.1f}s before using this command again.")
        except Exception as e:
            self.logger.error(f"Error in lyrics command: {e}")
            error_embed = discord.Embed(
                title="❌ Error",
                description=f"An unexpected error occurred: {str(e)}",
                color=discord.Color.red()
            )
            await loading_msg.edit(embed=error_embed)

    @commands.command(name='webui')
    async def webui(self, ctx):
        """Get the web UI URL for controlling music playback"""
        try:
            embed = discord.Embed(
                title="🎵 Music Bot Web UI",
                description="Control your music through our fancy web interface!",
                color=discord.Color.blue()
            )

            web_url = f"https://{os.getenv('REPLIT_DEV_DOMAIN')}"
            embed.add_field(
                name="🌐 Web Interface URL",
                value=f"[Click here to open]({web_url})",
                inline=False
            )

            features = (
                "✨ **Features:**\n"
                "• Live song progress\n"
                "• Volume control\n"
                "• Skip button\n"
                "• Current song info\n"
                "• Album artwork"
            )
            embed.add_field(name="Features", value=features, inline=False)

            await ctx.send(embed=embed)
        except Exception as e:
            self.logger.error(f"Error showing web UI info: {e}")
            await ctx.send("❌ An error occurred while getting web UI information.")

    @commands.Cog.listener()
    async def on_socket_response(self, msg):
        """Handle web UI socket events"""
        try:
            if msg.get("t") == "VOICE_STATE_UPDATE":
                player = self.players.get(int(msg["d"]["guild_id"]))
                if player:
                    player.update_web_ui()
        except Exception as e:
            self.logger.error(f"Error handling socket response: {e}")

    async def set_volume_web(self, ctx, volume: int):
        """Set volume from web UI"""
        try:
            if not ctx.voice_client:
                return False

            volume = max(0, min(100, volume))
            ctx.voice_client.source.volume = volume / 100
            return True
        except Exception as e:
            self.logger.error(f"Error setting volume from web: {e}")
            return False

    async def handle_skip_web(self, ctx):
        """Handle skip request from web UI"""
        try:
            if not ctx.voice_client or not ctx.voice_client.is_playing():
                return False
            ctx.voice_client.stop()
            return True
        except Exception as e:
            self.logger.error(f"Error handling web skip: {e}")
            return False

async def setup(bot):
    await bot.add_cog(MusicCommands(bot))