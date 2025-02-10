import discord
from discord.ext import commands
import logging
import asyncio
from typing import List, Optional

class AdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger('discord_bot')

    @commands.command(name='staffhelp')
    @commands.has_permissions(administrator=True)
    async def staff_help(self, ctx):
        """Show staff commands help"""
        embed = discord.Embed(
            title="👑 Staff Commands",
            description="✨ Welcome to the Administrative Control Panel ✨\nYour gateway to managing EduSphere with excellence!",
            color=discord.Color.light_blue()
        )

        # Member Management Commands
        member_commands = (
            "• **!mute** `<member> [reason]` - Temporarily restrict member's messaging ability\n"
            "• **!unmute** `<member>` - Restore member's messaging privileges\n"
            "• **!kick** `<member> [reason]` - Remove a member from the server\n"
            "• **!ban** `<member> [reason]` - Permanently ban a member\n"
            "• **!unban** `<user_id>` - Revoke a member's ban"
        )
        embed.add_field(
            name="🛡️ Member Management",
            value=member_commands,
            inline=False
        )

        # Channel Control Commands
        channel_commands = (
            "• **!announce** `-r <role> <message>` - Make an announcement with role ping\n"
            "  Example: `!announce -r @everyone New update!`\n"
            "• **!clear** `<amount>` - Clear specified number of messages"
        )
        embed.add_field(
            name="📢 Channel Controls",
            value=channel_commands,
            inline=False
        )

        # System Management Commands
        system_commands = (
            "• **!refresh** - Reload all bot extensions\n"
            "• **!ping** - Check bot's connection status"
        )
        embed.add_field(
            name="⚙️ System Management",
            value=system_commands,
            inline=False
        )

        embed.set_footer(text="EduSphere Staff Panel • Made with 💖 by Rohanpreet singh Pathania")
        await ctx.send(embed=embed)

    @commands.command(name='refresh')
    @commands.has_permissions(administrator=True)
    async def refresh(self, ctx):
        """Refresh bot by reloading all extensions"""
        loading_msg = await ctx.send("🔄 Reloading all extensions...")

        try:
            extensions = [
                'cogs.education_manager_new',
                'cogs.admin_commands'
            ]

            for extension in extensions:
                await self.bot.reload_extension(extension)
                self.logger.info(f"Successfully reloaded extension: {extension}")

            await loading_msg.edit(content="✨ All extensions and commands are loaded and working! ✨")

        except Exception as e:
            self.logger.error(f"Error refreshing bot: {e}")
            await loading_msg.edit(content=f"❌ Error refreshing bot: {str(e)}")

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
    await bot.add_cog(AdminCommands(bot))