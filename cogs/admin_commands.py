import discord
from discord.ext import commands
import logging
import asyncio
from typing import List, Optional

class AdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger('discord_bot')

    @commands.command(name='ping')
    async def ping(self, ctx):
        """Check bot latency"""
        latency = round(self.bot.latency * 1000)
        await ctx.send(f"🏓 Pong! Latency: {latency}ms")

    @commands.command(name='setupticket')
    @commands.has_permissions(administrator=True)
    async def setup_ticket(self, ctx, channel: discord.TextChannel = None):
        """Set up the ticket system in a channel"""
        channel = channel or ctx.channel
        embed = discord.Embed(
            title="Support Ticket System",
            description="Click the button below to create a support ticket!",
            color=discord.Color.blue()
        )

        class TicketButton(discord.ui.Button):
            def __init__(self):
                super().__init__(style=discord.ButtonStyle.primary, label="Create Ticket", emoji="🎫")

            async def callback(self, interaction):
                # Create ticket channel
                guild = interaction.guild
                category = discord.utils.get(guild.categories, name='Tickets')

                if category is None:
                    category = await guild.create_category('Tickets')

                channel_name = f'ticket-{interaction.user.name.lower()}'

                overwrites = {
                    guild.default_role: discord.PermissionOverwrite(read_messages=False),
                    interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                    guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
                }

                ticket_channel = await category.create_text_channel(name=channel_name, overwrites=overwrites)
                await interaction.response.send_message(f"Ticket created! Check {ticket_channel.mention}", ephemeral=True)

        view = discord.ui.View()
        view.add_item(TicketButton())
        await channel.send(embed=embed, view=view)

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

async def setup(bot):
    await bot.add_cog(AdminCommands(bot))