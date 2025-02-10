import discord
from discord.ext import commands
import logging
from typing import Optional, Union
import asyncio

class AdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger('discord_bot')
        # Define staff role IDs
        self.owner_role_id = 1337415762947604521
        self.mod_role_id = 1337415926164750386
        self.helper_role_id = 1337416072382386187

    def is_staff(self, member: discord.Member) -> bool:
        """Check if a member has any staff role"""
        return any(role.id in [self.owner_role_id, self.mod_role_id, self.helper_role_id] 
                  for role in member.roles)

    @commands.command(name='staffhelp')
    async def staff_help(self, ctx):
        """Show staff-only help menu"""
        if not self.is_staff(ctx.author):
            await ctx.send("❌ You don't have permission to use this command!")
            return

        help_embed = discord.Embed(
            title="👮 EduSphere Staff Commands",
            description="Complete list of staff commands",
            color=discord.Color.blue()
        )

        # Moderation Commands
        mod_commands = (
            "```\n"
            "!mute <member> [reason] - Mute a member\n"
            "!unmute <member> - Unmute a member\n"
            "!kick <member> [reason] - Kick a member\n"
            "!ban <member> [reason] - Ban a member\n"
            "!unban <user_id> - Unban a member\n"
            "!clear <amount> - Clear messages\n"
            "```"
        )
        help_embed.add_field(
            name="🛡️ Moderation Commands",
            value=mod_commands,
            inline=False
        )

        # System Commands
        system_commands = (
            "```\n"
            "!announce <message> - Make an announcement\n"
            "!refresh - Reload bot extensions\n"
            "!ping - Check bot latency\n"
            "```"
        )
        help_embed.add_field(
            name="⚙️ System Commands",
            value=system_commands,
            inline=False
        )

        help_embed.set_footer(text="EduSphere Staff Panel • Made with ❤️")
        await ctx.send(embed=help_embed)

    @commands.command(name='mute')
    async def mute_member(self, ctx, member: discord.Member, *, reason: Optional[str] = "No reason provided"):
        """Mute a member"""
        if not self.is_staff(ctx.author):
            await ctx.send("❌ You don't have permission to use this command!")
            return

        try:
            muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
            if not muted_role:
                # Create muted role if it doesn't exist
                muted_role = await ctx.guild.create_role(name="Muted")
                for channel in ctx.guild.channels:
                    await channel.set_permissions(muted_role, speak=False, send_messages=False)

            await member.add_roles(muted_role)
            embed = discord.Embed(
                title="🔇 Member Muted",
                description=f"{member.mention} has been muted\nReason: {reason}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Error muting member: {e}")
            await ctx.send("❌ An error occurred while muting the member.")

    @commands.command(name='unmute')
    async def unmute_member(self, ctx, member: discord.Member):
        """Unmute a member"""
        if not self.is_staff(ctx.author):
            await ctx.send("❌ You don't have permission to use this command!")
            return

        try:
            muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
            if muted_role in member.roles:
                await member.remove_roles(muted_role)
                embed = discord.Embed(
                    title="🔊 Member Unmuted",
                    description=f"{member.mention} has been unmuted",
                    color=discord.Color.green()
                )
                await ctx.send(embed=embed)
            else:
                await ctx.send("This member is not muted!")

        except Exception as e:
            self.logger.error(f"Error unmuting member: {e}")
            await ctx.send("❌ An error occurred while unmuting the member.")

    @commands.command(name='kick')
    async def kick_member(self, ctx, member: discord.Member, *, reason: Optional[str] = "No reason provided"):
        """Kick a member from the server"""
        if not self.is_staff(ctx.author):
            await ctx.send("❌ You don't have permission to use this command!")
            return

        try:
            await member.kick(reason=reason)
            embed = discord.Embed(
                title="👢 Member Kicked",
                description=f"{member.mention} has been kicked\nReason: {reason}",
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Error kicking member: {e}")
            await ctx.send("❌ An error occurred while kicking the member.")

    @commands.command(name='ban')
    async def ban_member(self, ctx, member: discord.Member, *, reason: Optional[str] = "No reason provided"):
        """Ban a member from the server"""
        if not self.is_staff(ctx.author):
            await ctx.send("❌ You don't have permission to use this command!")
            return

        try:
            await member.ban(reason=reason)
            embed = discord.Embed(
                title="🔨 Member Banned",
                description=f"{member.mention} has been banned\nReason: {reason}",
                color=discord.Color.dark_red()
            )
            await ctx.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Error banning member: {e}")
            await ctx.send("❌ An error occurred while banning the member.")

    @commands.command(name='unban')
    async def unban_member(self, ctx, user_id: int):
        """Unban a member using their user ID"""
        if not self.is_staff(ctx.author):
            await ctx.send("❌ You don't have permission to use this command!")
            return

        try:
            user = await self.bot.fetch_user(user_id)
            await ctx.guild.unban(user)
            embed = discord.Embed(
                title="🔓 Member Unbanned",
                description=f"{user.name} has been unbanned",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)

        except discord.NotFound:
            await ctx.send("❌ User not found!")
        except Exception as e:
            self.logger.error(f"Error unbanning member: {e}")
            await ctx.send("❌ An error occurred while unbanning the member.")

    @commands.command(name='clear')
    async def clear_messages(self, ctx, amount: int = 5):
        """Clear a specified number of messages from the channel"""
        if not self.is_staff(ctx.author):
            await ctx.send("❌ You don't have permission to use this command!")
            return

        try:
            deleted = await ctx.channel.purge(limit=amount + 1)  # +1 to include command message
            embed = discord.Embed(
                title="🧹 Channel Cleaned",
                description=f"Successfully deleted {len(deleted)-1} messages",
                color=discord.Color.green()
            )
            msg = await ctx.send(embed=embed)
            await asyncio.sleep(5)
            await msg.delete()

        except Exception as e:
            self.logger.error(f"Error clearing messages: {e}")
            await ctx.send("❌ An error occurred while clearing messages.")

    @commands.command(name='announce')
    async def make_announcement(self, ctx, *, message: str):
        """Make a server announcement"""
        if not self.is_staff(ctx.author):
            await ctx.send("❌ You don't have permission to use this command!")
            return

        try:
            embed = discord.Embed(
                title="📢 EduSphere Announcement",
                description=message,
                color=discord.Color.blue()
            )
            embed.set_footer(text=f"Announced by {ctx.author.name}")
            await ctx.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Error making announcement: {e}")
            await ctx.send("❌ An error occurred while making the announcement.")

    async def cog_command_error(self, ctx, error):
        """Handle command errors"""
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You don't have permission to use this command!")
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send("❌ Member not found!")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("❌ Invalid argument provided!")
        else:
            self.logger.error(f"Command error: {error}")
            await ctx.send("❌ An error occurred while executing the command.")

async def setup(bot):
    await bot.add_cog(AdminCommands(bot))
