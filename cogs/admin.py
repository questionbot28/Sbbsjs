import discord
from discord.ext import commands
import logging
import asyncio

class Admin(commands.Cog):
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

            # Load all extensions
            extensions = [
                'cogs.education_manager_new',  # Using the new education manager
                'cogs.admin'
            ]

            for extension in extensions:
                await self.bot.load_extension(extension)
                self.logger.info(f"Successfully reloaded extension: {extension}")

            await loading_msg.edit(content="✨ All extensions and commands are loaded and working! ✨")

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

async def setup(bot):
    await bot.add_cog(Admin(bot))