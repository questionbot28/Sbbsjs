import discord
from discord.ext import commands
import logging
from typing import Dict, Optional
from datetime import datetime, timedelta

class InviteManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger('discord_bot')
        # Enhanced invite tracking
        self.invites: Dict[int, Dict] = {}  # {user_id: {count: int, created_at: datetime, leaves: int, fakes: int, history: list}}
        self.guild_invites = {}  # Store guild invites for tracking
        self.invite_history = {}  # {invite_code: {inviter_id: int, joined_users: list, left_users: list}}

    async def cache_invites(self):
        """Cache all guild invites on startup"""
        for guild in self.bot.guilds:
            try:
                self.guild_invites[guild.id] = await guild.invites()
            except Exception as e:
                self.logger.error(f"Failed to cache invites for guild {guild.name}: {e}")

    def _get_time_based_invites(self, user_id: int) -> dict:
        """Get time-based invite statistics for a user"""
        now = datetime.now()
        history = self.invites.get(user_id, {}).get('history', [])

        today = sum(1 for date in history if (now - date).days == 0)
        last_3_days = sum(1 for date in history if (now - date).days <= 3)
        last_week = sum(1 for date in history if (now - date).days <= 7)

        return {
            'today': today,
            'last_3_days': last_3_days,
            'last_week': last_week
        }

    @commands.Cog.listener()
    async def on_ready(self):
        """Cache invites when bot is ready"""
        await self.cache_invites()

    @commands.Cog.listener()
    async def on_invite_create(self, invite):
        """Update invite cache when a new invite is created"""
        try:
            if invite.guild.id in self.guild_invites:
                self.guild_invites[invite.guild.id].append(invite)
                # Initialize invite history
                self.invite_history[invite.code] = {
                    'inviter_id': invite.inviter.id,
                    'joined_users': [],
                    'left_users': []
                }
        except Exception as e:
            self.logger.error(f"Error handling invite creation: {e}")

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """Track when invited members leave"""
        try:
            for invite_code, data in self.invite_history.items():
                if member.id in data['joined_users']:
                    inviter_id = data['inviter_id']
                    if inviter_id in self.invites:
                        self.invites[inviter_id]['leaves'] = self.invites[inviter_id].get('leaves', 0) + 1
                    data['left_users'].append(member.id)
                    self.logger.info(f"Member {member.name} left (invited by {inviter_id})")
                    break
        except Exception as e:
            self.logger.error(f"Error tracking member leave: {e}")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Track which invite was used when a member joins"""
        try:
            invites_before = self.guild_invites.get(member.guild.id, [])
            invites_after = await member.guild.invites()
            self.guild_invites[member.guild.id] = invites_after

            # Find used invite
            for invite in invites_before:
                matched_invite = next((inv for inv in invites_after if inv.id == invite.id), None)
                if matched_invite and matched_invite.uses > invite.uses:
                    inviter_id = invite.inviter.id
                    if inviter_id not in self.invites:
                        self.invites[inviter_id] = {
                            'count': 0,
                            'leaves': 0,
                            'fakes': 0,
                            'created_at': datetime.now(),
                            'history': []
                        }

                    # Update inviter stats
                    self.invites[inviter_id]['count'] += 1
                    self.invites[inviter_id]['history'].append(datetime.now())

                    # Update invite history
                    if invite.code in self.invite_history:
                        self.invite_history[invite.code]['joined_users'].append(member.id)

                    self.logger.info(f"Member {member.name} joined using {invite.inviter.name}'s invite")
                    break

        except Exception as e:
            self.logger.error(f"Error tracking member join invite: {e}")

    @commands.command(name='invites')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def check_invites(self, ctx):
        """Check your current invite count with detailed statistics"""
        try:
            user_data = self.invites.get(ctx.author.id, {
                'count': 0,
                'leaves': 0,
                'fakes': 0,
                'created_at': datetime.now(),
                'history': []
            })

            time_stats = self._get_time_based_invites(ctx.author.id)
            valid_invites = user_data['count'] - user_data['leaves'] - user_data['fakes']

            embed = discord.Embed(
                title="📩 Invitation Hub 📩",
                description=f"Hey {ctx.author.mention}, here's your invite breakdown! 🎉",
                color=discord.Color.blue()
            )

            main_stats = (
                f"👥 Total Invites: {user_data['count']}\n"
                f"✅ Successful Joins: {valid_invites}\n"
                f"❌ Leaves: {user_data['leaves']}\n"
                f"🚫 Fake/Invalid: {user_data['fakes']}\n"
            )
            embed.add_field(name="📊 Overall Statistics", value=main_stats, inline=False)

            time_based_stats = (
                f"📆 Today's Invites: {time_stats['today']}\n"
                f"📅 Last 3 Days: {time_stats['last_3_days']}\n"
                f"🗓 Last 7 Days: {time_stats['last_week']}\n"
            )
            embed.add_field(name="⏰ Time-Based Statistics", value=time_based_stats, inline=False)

            embed.set_footer(text="🏆 Keep inviting and climb the leaderboard! 🚀")
            await ctx.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Error checking invites: {e}")
            await ctx.send("❌ An error occurred while checking your invites.")

    @commands.command(name='invite-stats')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def invite_stats(self, ctx, member: discord.Member = None):
        """Check detailed invite statistics for a user"""
        try:
            member = member or ctx.author
            user_data = self.invites.get(member.id, {
                'count': 0,
                'leaves': 0,
                'fakes': 0,
                'created_at': datetime.now(),
                'history': []
            })

            time_stats = self._get_time_based_invites(member.id)
            valid_invites = user_data['count'] - user_data['leaves'] - user_data['fakes']

            embed = discord.Embed(
                title=f"📊 Invite Stats for {member.display_name} 📊",
                description=f"Want to check someone's invite power? Here's the invite breakdown for {member.mention}!",
                color=discord.Color.blue()
            )

            main_stats = (
                f"👥 Total Invites: {user_data['count']}\n"
                f"✅ Successful Joins: {valid_invites}\n"
                f"❌ Leaves: {user_data['leaves']}\n"
                f"🚫 Fake/Invalid: {user_data['fakes']}\n"
            )
            embed.add_field(name="📊 Overall Statistics", value=main_stats, inline=False)

            time_based_stats = (
                f"📆 Today's Invites: {time_stats['today']}\n"
                f"📅 Last 3 Days: {time_stats['last_3_days']}\n"
                f"🗓 Last 7 Days: {time_stats['last_week']}\n"
            )
            embed.add_field(name="⏰ Time-Based Statistics", value=time_based_stats, inline=False)

            embed.set_footer(text="🔍 Stay ahead and invite more to lead the scoreboard! 🏆")
            await ctx.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Error checking invite stats: {e}")
            await ctx.send("❌ An error occurred while checking invite stats.")

    @commands.command(name='invite-history')
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def invite_history(self, ctx, member: discord.Member = None):
        """View detailed invite history for a user"""
        try:
            member = member or ctx.author
            user_data = self.invites.get(member.id, {
                'count': 0,
                'leaves': 0,
                'fakes': 0,
                'created_at': datetime.now(),
                'history': []
            })

            history = user_data['history']
            first_invite = min(history) if history else None
            last_invite = max(history) if history else None

            embed = discord.Embed(
                title=f"📜 Invite History for {member.display_name} 📜",
                description=f"Curious about {member.mention}'s invite history? Here's the full log!",
                color=discord.Color.blue()
            )

            date_info = (
                f"🔗 First Invite: {first_invite.strftime('%Y-%m-%d') if first_invite else 'No invites yet'}\n"
                f"⏳ Last Invite: {last_invite.strftime('%Y-%m-%d') if last_invite else 'No invites yet'}\n"
                f"📊 Total Invites Used: {user_data['count']}\n"
            )
            embed.add_field(name="📅 Timeline", value=date_info, inline=False)

            # Add warning about fake invites
            embed.add_field(
                name="⚠️ Note",
                value="Fake and left invites are not counted in rankings.",
                inline=False
            )

            embed.set_footer(text="📢 Keep inviting and make history in the leaderboard! 🚀")
            await ctx.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Error checking invite history: {e}")
            await ctx.send("❌ An error occurred while checking invite history.")

    @commands.command(name='invite-leaderboard')
    @commands.cooldown(1, 30, commands.BucketType.guild)
    async def invite_leaderboard(self, ctx):
        """Display the server's invite leaderboard with detailed statistics"""
        try:
            sorted_invites = sorted(
                self.invites.items(),
                key=lambda x: x[1]['count'] - x[1]['leaves'] - x[1]['fakes'],
                reverse=True
            )[:10]  # Top 10

            embed = discord.Embed(
                title="🏆 Invite Leaderboard 🏆",
                description="Who's the ultimate inviter? Let's check the top inviters of all time! 🎖",
                color=discord.Color.gold()
            )

            medals = ["🥇", "🥈", "🥉"]
            for i, (user_id, data) in enumerate(sorted_invites[:3], 1):
                member = ctx.guild.get_member(user_id)
                if member:
                    valid_invites = data['count'] - data['leaves'] - data['fakes']
                    embed.add_field(
                        name=f"{medals[i-1]} {i}st Place: {member.display_name}",
                        value=f"✨ {valid_invites} valid invites",
                        inline=False
                    )

            if len(sorted_invites) > 3:
                other_ranks = []
                for i, (user_id, data) in enumerate(sorted_invites[3:], 4):
                    member = ctx.guild.get_member(user_id)
                    if member:
                        valid_invites = data['count'] - data['leaves'] - data['fakes']
                        other_ranks.append(f"{i}. {member.display_name} - {valid_invites} invites")

                if other_ranks:
                    embed.add_field(
                        name="🎖 4th - 10th Place",
                        value="\n".join(other_ranks),
                        inline=False
                    )

            embed.set_footer(text="🔥 Want to see your name here? Start inviting now!")
            await ctx.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Error displaying leaderboard: {e}")
            await ctx.send("❌ An error occurred while displaying the leaderboard.")

    @commands.command(name='addinv')
    @commands.has_permissions(administrator=True)
    async def add_invites(self, ctx, member: discord.Member, amount: int):
        """Add invites to a user's count"""
        try:
            if amount <= 0:
                await ctx.send("❌ Please specify a positive number of invites!")
                return

            if member.id not in self.invites:
                self.invites[member.id] = {'count': 0, 'leaves': 0, 'fakes': 0, 'created_at': datetime.now(), 'history': []}

            # Update invites
            self.invites[member.id]['count'] += amount

            # Get updated stats
            user_data = self.invites[member.id]
            valid_invites = user_data['count'] - user_data['leaves'] - user_data['fakes']

            # Create engaging embed
            embed = discord.Embed(
                title="➕ Add Invites ➕",
                description=f"Hey {ctx.author.mention}, you've added {amount} invites to {member.mention}! 🎉",
                color=discord.Color.green()
            )

            stats = (
                f"📈 Updated Invite Stats for {member.mention}:\n"
                f"👥 Total Invites: {user_data['count']}\n"
                f"✅ Successful Joins: {valid_invites}\n"
                f"❌ Leaves: {user_data['leaves']}\n"
                f"🚫 Fake/Invalid: {user_data['fakes']}\n"
            )
            embed.add_field(name="Updated Statistics", value=stats, inline=False)
            embed.set_footer(text="🏆 Boost your friends and help them climb the leaderboard! 🚀")

            await ctx.send(embed=embed)
            self.logger.info(f"Added {amount} invites to user {member.name}")
        except Exception as e:
            self.logger.error(f"Error adding invites: {e}")
            await ctx.send("❌ An error occurred while adding invites.")

    @commands.command(name='removeinv')
    @commands.has_permissions(administrator=True)
    async def remove_invites(self, ctx, member: discord.Member, amount: int):
        """Remove invites from a user's count"""
        try:
            if amount <= 0:
                await ctx.send("❌ Please specify a positive number of invites!")
                return

            if member.id not in self.invites:
                await ctx.send("❌ This user has no recorded invites!")
                return

            # Update invites
            self.invites[member.id]['count'] = max(0, self.invites[member.id]['count'] - amount)

            # Get updated stats
            user_data = self.invites[member.id]
            valid_invites = user_data['count'] - user_data['leaves'] - user_data['fakes']

            # Create engaging embed
            embed = discord.Embed(
                title="🛑 Remove Invites 🛑",
                description=f"Hey {ctx.author.mention}, you've removed {amount} invites from {member.mention}.",
                color=discord.Color.red()
            )

            stats = (
                f"📉 Updated Invite Stats for {member.mention}:\n"
                f"👥 Total Invites: {user_data['count']}\n"
                f"✅ Successful Joins: {valid_invites}\n"
                f"❌ Leaves: {user_data['leaves']}\n"
                f"🚫 Fake/Invalid: {user_data['fakes']}\n"
            )
            embed.add_field(name="Updated Statistics", value=stats, inline=False)
            embed.set_footer(text="⚠️ Use this command wisely to maintain fair rankings!")

            await ctx.send(embed=embed)
            self.logger.info(f"Removed {amount} invites from user {member.name}")
        except Exception as e:
            self.logger.error(f"Error removing invites: {e}")
            await ctx.send("❌ An error occurred while removing invites.")

    @commands.command(name='reset-invites')
    @commands.has_permissions(administrator=True)
    async def reset_invites(self, ctx, member: discord.Member):
        """Reset a user's invite count"""
        try:
            if member.id in self.invites:
                self.invites[member.id]['count'] = 0
                embed = discord.Embed(
                    title="🔄 Reset Invites 🔄",
                    description=f"{ctx.author.mention} has reset {member.mention}'s invites! 🧹",
                    color=discord.Color.orange()
                )
                embed.add_field(
                    name="Reset Status",
                    value=f"📉 All invite data has been wiped for {member.mention}.\n"
                          f"🆕 They're starting fresh with 0 invites!",
                    inline=False
                )
                embed.set_footer(text="⚠️ Be careful! This action is irreversible.")

                await ctx.send(embed=embed)
                self.logger.info(f"Reset invites for user {member.name}")
            else:
                await ctx.send("❌ This user has no recorded invites!")
        except Exception as e:
            self.logger.error(f"Error resetting invites: {e}")
            await ctx.send("❌ An error occurred while resetting invites.")

    @commands.command(name='fake-invite-check')
    @commands.has_permissions(administrator=True)
    async def fake_invite_check(self, ctx, member: discord.Member):
        """Check for potential fake invites"""
        try:
            if member.id not in self.invites:
                await ctx.send("❌ This user has no recorded invites!")
                return

            user_data = self.invites[member.id]
            total_invites = user_data['count']
            fake_invites = user_data['fakes']
            suspicious_percentage = (fake_invites / total_invites * 100) if total_invites > 0 else 0

            embed = discord.Embed(
                title="🚨 Fake Invite Check 🚨",
                description=f"🔍 Analyzing {member.mention}'s invite activity...",
                color=discord.Color.orange()
            )

            analysis = (
                f"📊 Fake/Invalid Invites: {fake_invites}\n"
                f"❌ Percentage of Suspicious Invites: {suspicious_percentage:.1f}%\n"
                f"📢 Total Invites Checked: {total_invites}\n\n"
                f"🛑 If the percentage is high, this user may be using fake invites!"
            )
            embed.add_field(name="Analysis Results", value=analysis, inline=False)
            embed.add_field(
                name="Account Information",
                value=f"📅 Account Age: {(datetime.now() - member.created_at).days} days",
                inline=False
            )
            embed.set_footer(text="⚠️ Admins, take action if needed! 🚨")

            await ctx.send(embed=embed)
            self.logger.info(f"Performed fake invite check for user {member.name}")
        except Exception as e:
            self.logger.error(f"Error checking fake invites: {e}")
            await ctx.send("❌ An error occurred while checking for fake invites.")

    @commands.command(name='helpinv')
    @commands.cooldown(1, 30, commands.BucketType.user)  # Once every 30 seconds per user
    async def help_invites(self, ctx):
        """Display the invite tracking help menu"""
        try:
            embed = discord.Embed(
                title="🎟️ INVITE TRACKER COMMAND CENTER 🎟️",
                description="🚀 Ready to build your empire? Track, manage, and dominate the leaderboard!",
                color=discord.Color.blue()
            )

            # Invite Commands Section
            invite_commands = (
                "> 🌟 !invites – See your invite kingdom! 👑 Who joined because of you?\n"
                "🔎 !invite-stats @user – Spy on a user's invite power! Are they a real recruiter? 🕵️‍♂️\n"
                "📜 !invite-history @user – Unveil the history of invites! Who came, who left? 👀\n"
                "🏆 !invite-leaderboard – The ultimate race! Who's ruling the invite game? ⚡"
            )
            embed.add_field(
                name="━━━━━━━━━━━ ✦ 📊 INVITE COMMANDS ✦ ━━━━━━━━━━━",
                value=invite_commands,
                inline=False
            )

            # Admin Commands Section
            admin_commands = (
                "> ➕ !addinv @user <number> – Bless a user with extra invites! 🎁\n"
                "➖ !removeinv @user <number> – Take back invites from a user! ❌\n"
                "🔄 !reset-invites @user – Wipe someone's invite count! Fresh start! 🌪️\n"
                "🚨 !fake-invite-check @user – Exposing the frauds! Not on our watch! 🕶️"
            )
            embed.add_field(
                name="━━━━━━━━━━━ ✦ 🛠️ ADMIN COMMANDS ✦ ━━━━━━━━━━━",
                value=admin_commands,
                inline=False
            )

            # Extra Info Section
            extra_info = (
                "📨 Want to be the Top Inviter? Start now!\n"
                "🎁 More invites = More rewards!\n"
                "📢 Use /invite to get your personal invite link & grow the server!\n\n"
                "⚡ Who will rise? Who will fall? The leaderboard awaits! 🏆"
            )
            embed.add_field(
                name="━━━━━━━━━━━ ✦ 🔥 EXTRA INFO ✦ ━━━━━━━━━━━",
                value=extra_info,
                inline=False
            )

            await ctx.send(embed=embed)
            self.logger.info(f"Help menu displayed for user {ctx.author.name}")
        except Exception as e:
            self.logger.error(f"Error displaying help menu: {e}")
            await ctx.send("❌ An error occurred while displaying the help menu.")


    @help_invites.error
    @check_invites.error
    @invite_stats.error
    @invite_history.error
    @invite_leaderboard.error
    @add_invites.error
    @remove_invites.error
    @reset_invites.error
    @fake_invite_check.error
    async def on_command_error(self, ctx, error):
        """Handle common command errors"""
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"⏳ Please wait {error.retry_after:.1f} seconds before using this command again!")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You don't have permission to use this command!")
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send("❌ Member not found! Please mention a valid server member.")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("❌ Invalid argument provided. Please check your input.")
        else:
            self.logger.error(f"Unhandled command error: {error}")
            await ctx.send("❌ An error occurred while processing your command.")

async def setup(bot):
    await bot.add_cog(InviteManager(bot))