import discord
from discord.ext import commands
import logging
import asyncio
from typing import Optional, Union

class StaffCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger('discord_bot')
        # Define staff role IDs
        self.owner_role_id = 1337415762947604521
        self.mod_role_id = 1337415926164750386
        self.helper_role_id = 1337416072382386187
        self.staff_cmd_channel_id = 1338360696873680999
        self.mod_log_channel_id = 1337415561537257582
        self.announcement_channel_id = 1337410366401151038

    def is_staff(self, member: discord.Member) -> bool:
        """Check if a member has any staff role"""
        return any(role.id in [self.owner_role_id, self.mod_role_id, self.helper_role_id]
                  for role in member.roles)

    async def log_staff_action(self, staff_member: discord.Member, action: str, details: str = None):
        """Log staff actions to mod log channel"""
        try:
            log_channel = self.bot.get_channel(self.mod_log_channel_id)
            if not log_channel:
                return

            log_embed = discord.Embed(
                title="👮‍♂️ Staff Action Log",
                color=discord.Color.blue(),
                timestamp=discord.utils.utcnow()
            )

            log_embed.add_field(
                name="Staff Member",
                value=f"{staff_member.mention} ({staff_member.name})",
                inline=False
            )

            log_embed.add_field(
                name="Action",
                value=action,
                inline=False
            )

            if details:
                log_embed.add_field(
                    name="Details",
                    value=details,
                    inline=False
                )

            log_embed.set_footer(text=f"Staff ID: {staff_member.id}")
            await log_channel.send(embed=log_embed)

        except Exception as e:
            self.logger.error(f"Error logging staff action: {e}")

    @commands.command(name='staffhelp')
    async def staff_help(self, ctx):
        """Show enhanced staff-only help menu"""
        if ctx.channel.id != self.staff_cmd_channel_id:
            await ctx.send("❌ This command can only be used in the staff commands channel!")
            return

        if not self.is_staff(ctx.author):
            await ctx.send("❌ You don't have permission to use this command!")
            return

        help_embed = discord.Embed(
            title="🎓 EduSphere Staff Panel",
            description="✨ Welcome to the Administrative Control Panel ✨\nYour gateway to managing EduSphere with excellence!",
            color=discord.Color.blue()
        )

        # Member Management Section
        member_commands = (
            "**🛡️ Member Management**\n\n"
            "• **!mute** `<member> [reason]` - Temporarily restrict member's messaging ability\n"
            "• **!unmute** `<member>` - Restore member's messaging privileges\n"
            "• **!kick** `<member> [reason]` - Remove a member from the server\n"
            "• **!ban** `<member> [reason]` - Permanently ban a member\n"
            "• **!unban** `<user_id>` - Revoke a member's ban\n"
        )
        help_embed.add_field(
            name="👥 Member Controls",
            value=member_commands,
            inline=False
        )

        # Channel Management Section
        channel_commands = (
            "**📢 Channel Controls**\n\n"
            "• **!announce** `-r <role> <message>` - Make an announcement with role ping\n"
            "  Example: `!announce -r @everyone New update!`\n"
            "• **!clear** `<amount>` - Clear specified number of messages\n"
        )
        help_embed.add_field(
            name="💬 Channel Management",
            value=channel_commands,
            inline=False
        )

        help_embed.set_footer(text="EduSphere Staff Panel • Made with 💖 by Rohanpreet singh Pathania")
        await ctx.send(embed=help_embed)

        # Log the staff help command usage
        await self.log_staff_action(
            ctx.author,
            "Used !staffhelp command",
            f"Channel: {ctx.channel.mention}"
        )

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

            # Send announcement
            sent_message = None
            if ping:
                sent_message = await announcement_channel.send(ping, embed=announcement_embed)
            else:
                sent_message = await announcement_channel.send(embed=announcement_embed)

            # Log the announcement
            await self.log_staff_action(
                ctx.author,
                "Made an announcement",
                f"Channel: {announcement_channel.mention}\nMessage: {message[:100]}{'...' if len(message) > 100 else ''}"
            )

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

            # Log the clear action
            await self.log_staff_action(
                ctx.author,
                "Cleared messages",
                f"Channel: {ctx.channel.mention}\nAmount: {len(deleted)-1} messages"
            )

            await asyncio.sleep(3)
            await msg.delete()
        except Exception as e:
            self.logger.error(f"Error clearing messages: {e}")
            await ctx.send("❌ An error occurred while clearing messages.")

async def setup(bot):
    await bot.add_cog(StaffCommands(bot))