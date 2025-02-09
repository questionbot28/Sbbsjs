import discord
from discord.ext import commands
import logging
import asyncio

class AdminCore(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger('discord_bot')

    @commands.command(name='refresh')
    @commands.has_permissions(administrator=True)
    async def refresh(self, ctx):
        """Refresh bot by reloading all extensions"""
        loading_msg = await ctx.send("🔄 Reloading all extensions...")

        try:
            # Unload all extensions first
            for extension in list(self.bot.extensions):
                await self.bot.unload_extension(extension)
                self.logger.info(f"Unloaded extension: {extension}")

            # Load all extensions
            extensions = [
                'cogs.education_core_v2',
                'cogs.admin_core'
            ]

            for extension in extensions:
                await self.bot.load_extension(extension)
                self.logger.info(f"Successfully reloaded extension: {extension}")

            await loading_msg.edit(content="✨ Successfully reloaded all extensions! Bot is ready to use. ✨")

        except Exception as e:
            self.logger.error(f"Error refreshing bot: {e}")
            await loading_msg.edit(content=f"❌ Error refreshing bot: {str(e)}")
            # Try to load back the extensions that were unloaded
            try:
                for extension in extensions:
                    if extension not in self.bot.extensions:
                        await self.bot.load_extension(extension)
            except Exception as reload_error:
                self.logger.error(f"Error reloading extensions after failure: {reload_error}")

    @commands.command(name='ping')
    async def ping(self, ctx):
        """Check bot's latency"""
        latency = round(self.bot.latency * 1000)
        ping_embed = discord.Embed(
            title="🏓 Pong!",
            description=f"Bot latency: {latency}ms",
            color=discord.Color.green() if latency < 200 else discord.Color.orange()
        )

        if latency < 100:
            status = "🟢 Excellent"
        elif latency < 200:
            status = "🟡 Good"
        else:
            status = "🔴 Poor"

        ping_embed.add_field(
            name="Connection Quality",
            value=status,
            inline=False
        )
        await ctx.send(embed=ping_embed)

async def setup(bot):
    await bot.add_cog(AdminCore(bot))
