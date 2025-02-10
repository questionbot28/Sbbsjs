import discord
from discord.ext import commands
import logging
from typing import Optional, Union
import asyncio

class EnhancedAdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger('discord_bot')
        # Define staff role IDs
        self.owner_role_id = 1337415762947604521
        self.mod_role_id = 1337415926164750386
        self.helper_role_id = 1337416072382386187
        self.announcement_channel_id = 1337410366401151038

    def is_staff(self, member: discord.Member) -> bool:
        """Check if a member has any staff role"""
        return any(role.id in [self.owner_role_id, self.mod_role_id, self.helper_role_id] 
                  for role in member.roles)

    @commands.command(name='staffhelp')
    async def staff_help(self, ctx):
        """Show enhanced staff-only help menu"""
        if not self.is_staff(ctx.author):
            await ctx.send("❌ You don't have permission to use this command!")
            return

        help_embed = discord.Embed(
            title="🎓 EduSphere Staff Panel",
            description="Complete guide to staff commands",
            color=discord.Color.blue()
        )

        # Member Management Section
        member_commands = (
            "```ansi\n"
            "[2;31m👥 Member Management[0m\n\n"
            "[2;34m!mute[0m [2;37m<member> [reason][0m\n"
            "└─ Silence a member temporarily\n\n"
            "[2;34m!unmute[0m [2;37m<member>[0m\n"
            "└─ Restore member's voice\n\n"
            "[2;34m!kick[0m [2;37m<member> [reason][0m\n"
            "└─ Remove member from server\n\n"
            "[2;34m!ban[0m [2;37m<member> [reason][0m\n"
            "└─ Ban member from server\n\n"
            "[2;34m!unban[0m [2;37m<user_id>[0m\n"
            "└─ Remove member's ban\n"
            "```"
        )
        help_embed.add_field(
            name="🛡️ Member Controls",
            value=member_commands,
            inline=False
        )

        # Channel Management Section
        channel_commands = (
            "```ansi\n"
            "[2;31m💬 Channel Management[0m\n\n"
            "[2;34m!announce[0m [2;37m-r <role> <message>[0m\n"
            "└─ Send announcement with role ping\n"
            "  [2;37mExample: !announce -r @everyone New update![0m\n\n"
            "[2;34m!clear[0m [2;37m<amount>[0m\n"
            "└─ Clear specified messages\n"
            "```"
        )
        help_embed.add_field(
            name="📢 Channel Controls",
            value=channel_commands,
            inline=False
        )

        # System Commands Section
        system_commands = (
            "```ansi\n"
            "[2;31m⚙️ System Controls[0m\n\n"
            "[2;34m!refresh[0m\n"
            "└─ Reload bot extensions\n\n"
            "[2;34m!ping[0m\n"
            "└─ Check bot latency\n"
            "```"
        )
        help_embed.add_field(
            name="🔧 System Controls",
            value=system_commands,
            inline=False
        )

        help_embed.set_footer(text="EduSphere Staff Panel • Made with 💖")
        await ctx.send(embed=help_embed)

    @commands.command(name='announce')
    async def make_announcement(self, ctx, *, content: str):
        """Make a server announcement with role ping support
        Usage: !announce -r @role Your announcement message"""
        if not self.is_staff(ctx.author):
            await ctx.send("❌ You don't have permission to use this command!")
            return

        try:
            # Get the announcement channel
            announcement_channel = self.bot.get_channel(self.announcement_channel_id)
            if not announcement_channel:
                await ctx.send("❌ Announcement channel not found!")
                return

            # Parse role mention if present
            if content.startswith('-r '):
                try:
                    # Split content into role mention and message
                    _, role_mention, *message_parts = content.split(maxsplit=2)
                    message = message_parts[0] if message_parts else ""
                    
                    # Convert role mention to actual role
                    if role_mention.startswith('<@&') and role_mention.endswith('>'):
                        role_id = int(role_mention[3:-1])
                        role = ctx.guild.get_role(role_id)
                        if role:
                            ping = role.mention
                        else:
                            await ctx.send("❌ Invalid role mention!")
                            return
                    else:
                        await ctx.send("❌ Please provide a valid role mention!")
                        return
                except Exception as e:
                    await ctx.send("❌ Invalid command format! Use: !announce -r @role Your message")
                    return
            else:
                ping = ""
                message = content

            # Create and send announcement embed
            embed = discord.Embed(
                title="📢 EduSphere Announcement",
                description=message,
                color=discord.Color.blue()
            )
            embed.set_author(
                name=ctx.author.display_name,
                icon_url=ctx.author.avatar.url if ctx.author.avatar else None
            )
            embed.set_footer(text=f"Announced at {ctx.message.created_at.strftime('%Y-%m-%d %H:%M:%S')}")

            # Send announcement
            if ping:
                await announcement_channel.send(ping, embed=embed)
            else:
                await announcement_channel.send(embed=embed)

            # Send confirmation
            confirm_embed = discord.Embed(
                title="✅ Announcement Sent!",
                description="Your announcement has been sent to the announcements channel.",
                color=discord.Color.green()
            )
            await ctx.send(embed=confirm_embed)

        except Exception as e:
            self.logger.error(f"Error making announcement: {e}")
            await ctx.send("❌ An error occurred while making the announcement.")

    # [Other admin commands remain the same as before]

async def setup(bot):
    await bot.add_cog(EnhancedAdminCommands(bot))
