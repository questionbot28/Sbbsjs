import discord
from discord.ext import commands
import aiohttp
import xml.etree.ElementTree as ET

class MusicCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = bot.logger

    async def get_lyrics(self, song_name: str) -> str:
        """Get lyrics using ChartLyrics API with enhanced search"""
        # URL encode the search query
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
                            # Provide helpful suggestions for numeric/special songs
                            suggestion_msg = (
                                f"❌ No lyrics found for '{song_name}'. Try:\n"
                                "• Adding the artist name (e.g., '295 Sidhu Moose Wala')\n"
                                "• Using the full song title\n"
                                "• Checking for typos"
                            )
                            return suggestion_msg

                        # Get the first result
                        first_result = search_results[0]

                        # Safely extract text values with fallbacks
                        song_title = first_result.find("Song")
                        song_title = song_title.text if song_title is not None else "Unknown Title"

                        artist = first_result.find("Artist")
                        artist = artist.text if artist is not None else "Unknown Artist"

                        lyrics_url = first_result.find("LyricUrl")
                        if lyrics_url is None or not lyrics_url.text:
                            return "❌ No lyrics URL available for this song."

                        lyrics_url = lyrics_url.text

                        # Log successful results
                        self.logger.info(f"Found lyrics for: {song_title} by {artist}")

                        # Create a rich embed response
                        return {
                            "title": song_title,
                            "artist": artist,
                            "url": lyrics_url,
                            "query": song_name  # Include original query
                        }

                    except ET.ParseError as e:
                        self.logger.error(f"XML parsing error: {e}")
                        self.logger.error(f"Raw XML data: {data[:200]}...")  # Log first 200 chars
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
        """Get lyrics for a song"""
        loading_msg = await ctx.send("🔍 Searching for lyrics...")

        try:
            # Log the search attempt
            self.logger.info(f"Searching lyrics for query: {query}")

            # Try to split artist and title if provided in format "title - artist"
            parts = query.split('-')
            if len(parts) == 2:
                song_title = parts[0].strip()
                artist = parts[1].strip()
                result = await self.get_lyrics(song_title) #This line was changed from self.search_song_info(song_title)
            else:
                result = await self.get_lyrics(query) #This line was changed from self.search_song_info(query)

        try:
            result = await self.get_lyrics(song_name)

            if isinstance(result, str):  # Error message
                error_embed = discord.Embed(
                    title="Lyrics Search Result",
                    description=result,
                    color=discord.Color.red()
                )
                await status_msg.edit(embed=error_embed)
                return

            # Create embed for successful result
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
            await status_msg.edit(embed=embed)

        except commands.CommandOnCooldown as e:
            await status_msg.edit(content=f"⏳ Please wait {e.retry_after:.1f}s before using this command again.")
        except Exception as e:
            self.logger.error(f"Error in lyrics command: {e}")
            error_embed = discord.Embed(
                title="❌ Error",
                description=f"An unexpected error occurred: {str(e)}",
                color=discord.Color.red()
            )
            await status_msg.edit(embed=error_embed)

async def setup(bot):
    """Setup function for the cog"""
    await bot.add_cog(MusicCommands(bot))