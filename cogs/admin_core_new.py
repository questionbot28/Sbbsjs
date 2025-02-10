import discord
from discord.ext import commands
import logging
import asyncio
from typing import Optional

class AdminCore(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger('discord_bot')

    @commands.command(name='clear')
    @commands.has_permissions(manage_messages=True)
    async def clear_messages(self, ctx, amount: int = 5):
        """Clear a specified number of messages from the channel"""
        try:
            await ctx.channel.purge(limit=amount + 1)  # +1 to include command message
            confirm_embed = discord.Embed(
                title="🧹 Channel Cleaned",
                description=f"Successfully deleted {amount} messages.",
                color=discord.Color.green()
            )
            await ctx.send(embed=confirm_embed, delete_after=5)
        except Exception as e:
            self.logger.error(f"Error clearing messages: {str(e)}")
            await ctx.send("❌ An error occurred while clearing messages.")

    @commands.command(name='announce')
    @commands.has_permissions(administrator=True)
    async def make_announcement(self, ctx, *, message: str):
        """Make an announcement with fancy formatting"""
        try:
            announce_embed = discord.Embed(
                title="📢 EduSphere Announcement",
                description=message,
                color=discord.Color.blue()
            )
            announce_embed.set_footer(text=f"Announced by {ctx.author.name}")
            await ctx.send(embed=announce_embed)
        except Exception as e:
            self.logger.error(f"Error making announcement: {str(e)}")
            await ctx.send("❌ An error occurred while making the announcement.")

    @commands.command(name='mute')
    @commands.has_permissions(manage_roles=True)
    async def mute_member(self, ctx, member: discord.Member, *, reason: Optional[str] = "No reason provided"):
        """Mute a member"""
        try:
            muted_role = discord.utils.get(ctx.guild.roles, name="Muted")

            if not muted_role:
                # Create muted role if it doesn't exist
                muted_role = await ctx.guild.create_role(
                    name="Muted",
                    reason="Created for muting members"
                )

                # Set permissions for the muted role
                for channel in ctx.guild.channels:
                    await channel.set_permissions(muted_role, speak=False, send_messages=False)

            await member.add_roles(muted_role)

            mute_embed = discord.Embed(
                title="🔇 Member Muted",
                description=f"{member.mention} has been muted.\nReason: {reason}",
                color=discord.Color.red()
            )
            await ctx.send(embed=mute_embed)

        except Exception as e:
            self.logger.error(f"Error muting member: {str(e)}")
            await ctx.send("❌ An error occurred while muting the member.")

    @commands.command(name='unmute')
    @commands.has_permissions(manage_roles=True)
    async def unmute_member(self, ctx, member: discord.Member):
        """Unmute a member"""
        try:
            muted_role = discord.utils.get(ctx.guild.roles, name="Muted")

            if not muted_role:
                await ctx.send("❌ No muted role found.")
                return

            await member.remove_roles(muted_role)

            unmute_embed = discord.Embed(
                title="🔊 Member Unmuted",
                description=f"{member.mention} has been unmuted.",
                color=discord.Color.green()
            )
            await ctx.send(embed=unmute_embed)

        except Exception as e:
            self.logger.error(f"Error unmuting member: {str(e)}")
            await ctx.send("❌ An error occurred while unmuting the member.")

    @commands.command(name='kick')
    @commands.has_permissions(kick_members=True)
    async def kick_member(self, ctx, member: discord.Member, *, reason: Optional[str] = "No reason provided"):
        """Kick a member from the server"""
        try:
            kick_embed = discord.Embed(
                title="👢 Member Kicked",
                description=f"{member.mention} has been kicked.\nReason: {reason}",
                color=discord.Color.red()
            )
            await member.kick(reason=reason)
            await ctx.send(embed=kick_embed)
        except Exception as e:
            self.logger.error(f"Error kicking member: {str(e)}")
            await ctx.send("❌ An error occurred while kicking the member.")

    @commands.command(name='ban')
    @commands.has_permissions(ban_members=True)
    async def ban_member(self, ctx, member: discord.Member, *, reason: Optional[str] = "No reason provided"):
        """Ban a member from the server"""
        try:
            ban_embed = discord.Embed(
                title="🔨 Member Banned",
                description=f"{member.mention} has been banned.\nReason: {reason}",
                color=discord.Color.dark_red()
            )
            await member.ban(reason=reason)
            await ctx.send(embed=ban_embed)
        except Exception as e:
            self.logger.error(f"Error banning member: {str(e)}")
            await ctx.send("❌ An error occurred while banning the member.")

    # Error handling for missing permissions
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You don't have the required permissions to use this command!")
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send("❌ Member not found!")

    @commands.command(name='refresh')
    @commands.has_permissions(administrator=True)
    async def refresh(self, ctx):
        """Refresh bot by reloading all extensions"""
        loading_msg = await ctx.send("🔄 Reloading all extensions...")

        try:
            extensions = [
                'cogs.education_manager_new',
                'cogs.subject_curriculum_new',
                'cogs.admin_core_new',
                'cogs.ticket_manager'
            ]

            for extension in extensions:
                await self.bot.reload_extension(extension)
                self.logger.info(f"Successfully reloaded extension: {extension}")

            await loading_msg.edit(content="✨ EduSphere Bot extensions are reloaded and ready! ✨")

        except Exception as e:
            self.logger.error(f"Error refreshing bot: {e}")
            await loading_msg.edit(content=f"❌ Error refreshing bot: {str(e)}")

    @commands.command(name='ping')
    async def ping(self, ctx):
        """Check bot's latency"""
        latency = round(self.bot.latency * 1000)
        ping_embed = discord.Embed(
            title="🏓 EduSphere Bot Status",
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