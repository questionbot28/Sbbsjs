import discord
from discord.ext import commands
import logging
from typing import Optional, Union
import asyncio

class StaffCommands(commands.Cog):
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
            description=(
                "```ansi\n"
                "[2;34m✨ Welcome to the Administrative Control Panel ✨[0m\n"
                "Your gateway to managing EduSphere with excellence!\n"
                "```"
            ),
            color=discord.Color.blue()
        )

        # Member Management Section
        member_commands = (
            "```ansi\n"
            "[2;31m🛡️ Member Management[0m\n\n"
            "[2;34m!mute[0m [2;37m<member> [reason][0m\n"
            "└─ Temporarily restrict member's messaging ability\n\n"
            "[2;34m!unmute[0m [2;37m<member>[0m\n"
            "└─ Restore member's messaging privileges\n\n"
            "[2;34m!kick[0m [2;37m<member> [reason][0m\n"
            "└─ Remove a member from the server\n\n"
            "[2;34m!ban[0m [2;37m<member> [reason][0m\n"
            "└─ Permanently ban a member\n\n"
            "[2;34m!unban[0m [2;37m<user_id>[0m\n"
            "└─ Revoke a member's ban\n"
            "```"
        )
        help_embed.add_field(
            name="👥 Member Controls",
            value=member_commands,
            inline=False
        )

        # Channel Management Section
        channel_commands = (
            "```ansi\n"
            "[2;31m📢 Channel Controls[0m\n\n"
            "[2;34m!announce[0m [2;37m-r <role> <message>[0m\n"
            "└─ Make an announcement with role ping\n"
            "[2;37m  Example: !announce -r @everyone New update![0m\n\n"
            "[2;34m!clear[0m [2;37m<amount>[0m\n"
            "└─ Clear specified number of messages\n"
            "```"
        )
        help_embed.add_field(
            name="💬 Channel Management",
            value=channel_commands,
            inline=False
        )

        # System Management Section
        system_commands = (
            "```ansi\n"
            "[2;31m⚙️ System Management[0m\n\n"
            "[2;34m!refresh[0m\n"
            "└─ Reload all bot extensions\n\n"
            "[2;34m!ping[0m\n"
            "└─ Check bot's connection status\n"
            "```"
        )
        help_embed.add_field(
            name="🔧 System Controls",
            value=system_commands,
            inline=False
        )

        help_embed.set_footer(text="EduSphere Staff Panel • Made with 💖 by Rohanpreet singh Pathania")
        await ctx.send(embed=help_embed)

    @commands.command(name='announce')
    async def announce(self, ctx, *, content: str):
        """Make a server announcement with role ping support
        Usage: !announce -r @role Your announcement message"""
        if not self.is_staff(ctx.author):
            await ctx.send("❌ You don't have permission to use this command!")
            return

        try:
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

            # Create announcement embed
            announcement_embed = discord.Embed(
                title="📢 EduSphere Announcement",
                description=message,
                color=discord.Color.blue()
            )
            
            announcement_embed.set_author(
                name=ctx.author.display_name,
                icon_url=ctx.author.avatar.url if ctx.author.avatar else None
            )
            
            current_time = ctx.message.created_at.strftime('%Y-%m-%d %H:%M:%S')
            announcement_embed.set_footer(
                text=f"Announced by {ctx.author.name} • {current_time}"
            )

            # Send announcement
            if ping:
                await announcement_channel.send(ping, embed=announcement_embed)
            else:
                await announcement_channel.send(embed=announcement_embed)

            # Send confirmation
            confirm_embed = discord.Embed(
                title="✅ Announcement Sent!",
                description=f"Your announcement has been sent to {announcement_channel.mention}",
                color=discord.Color.green()
            )
            await ctx.send(embed=confirm_embed)

        except Exception as e:
            self.logger.error(f"Error making announcement: {e}")
            await ctx.send("❌ An error occurred while making the announcement.")

    @commands.command(name='clear')
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int):
        """Clear a specified number of messages"""
        if amount < 1:
            await ctx.send("❌ Please specify a positive number of messages to clear!")
            return

        try:
            deleted = await ctx.channel.purge(limit=amount + 1)
            msg = await ctx.send(f"✨ Successfully cleared {len(deleted)-1} messages!")
            await asyncio.sleep(3)
            await msg.delete()
        except Exception as e:
            self.logger.error(f"Error clearing messages: {e}")
            await ctx.send("❌ An error occurred while clearing messages.")

    @commands.command(name='ping')
    @commands.has_permissions(administrator=True)
    async def ping(self, ctx):
        """Check bot's latency"""
        latency = round(self.bot.latency * 1000)
        
        if latency < 100:
            color = discord.Color.green()
            status = "🟢 Excellent"
        elif latency < 200:
            color = discord.Color.gold()
            status = "🟡 Good"
        else:
            color = discord.Color.red()
            status = "🔴 Poor"

        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"Bot Latency: {latency}ms",
            color=color
        )
        embed.add_field(name="Connection Status", value=status)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(StaffCommands(bot))
