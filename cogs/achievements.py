import discord
from discord.ext import commands
import logging
from typing import Dict, List, Set
import json
import os
from datetime import datetime
import sqlite3
import asyncio

class Achievement:
    def __init__(self, id: str, name: str, description: str, emoji: str, points: int, role_name: str = None, secret: bool = False):
        self.id = id
        self.name = name
        self.description = description
        self.emoji = emoji
        self.points = points
        self.role_name = role_name
        self.secret = secret

class Achievements(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger('discord_bot')
        # Initialize XP system
        self.xp_cooldown = {}
        self.setup_database()

        self.achievements = {
            # Education Achievements
            "first_question": Achievement(
                "first_question",
                "Curious Mind",
                "Ask your first practice question",
                "🎯",
                10,
                "Curious Mind"
            ),
            "knowledge_seeker": Achievement(
                "knowledge_seeker",
                "Knowledge Seeker",
                "Use practice questions from 5 different subjects",
                "📚",
                50,
                "Knowledge Seeker"
            ),
            "master_student": Achievement(
                "master_student",
                "Master Student",
                "Complete 100 practice questions",
                "🎓",
                100,
                "Master Student"
            ),

            # Music Achievements
            "music_lover": Achievement(
                "music_lover",
                "Music Enthusiast",
                "Play your first song",
                "🎵",
                10,
                "Music Enthusiast"
            ),
            "playlist_master": Achievement(
                "playlist_master",
                "Playlist Master",
                "Create a queue with 10 songs",
                "🎶",
                30,
                "Playlist Master"
            ),

            # AI Interaction Achievements
            "ai_explorer": Achievement(
                "ai_explorer",
                "AI Explorer",
                "Have your first AI conversation",
                "🤖",
                20,
                "AI Explorer"
            ),
            "deep_thinker": Achievement(
                "deep_thinker",
                "Deep Thinker",
                "Ask 50 questions to AI",
                "🧠",
                75,
                "Deep Thinker"
            ),

            # Secret Achievements
            "night_owl": Achievement(
                "night_owl",
                "Night Owl",
                "Study after midnight",
                "🦉",
                25,
                "Night Owl",
                True
            ),
            "speed_learner": Achievement(
                "speed_learner",
                "Speed Learner",
                "Complete 5 questions in under 5 minutes",
                "⚡",
                50,
                "Speed Learner",
                True
            )
        }
        self.user_achievements = {}
        self.load_achievements()
        self.logger.info("Achievements system initialized")

    def setup_database(self):
        """Initialize SQLite database for XP system"""
        try:
            os.makedirs('data', exist_ok=True)
            self.db = sqlite3.connect('data/user_data.db')
            cursor = self.db.cursor()

            # Create XP table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_xp (
                    user_id TEXT PRIMARY KEY,
                    xp INTEGER DEFAULT 0,
                    level INTEGER DEFAULT 1,
                    last_xp_gain TIMESTAMP
                )
            ''')
            self.db.commit()
            self.logger.info("XP database initialized successfully")
        except Exception as e:
            self.logger.error(f"Error setting up database: {str(e)}")

    def calculate_level(self, xp: int) -> int:
        """Calculate level based on XP"""
        return int((xp / 100) ** 0.5) + 1

    def calculate_xp_for_level(self, level: int) -> int:
        """Calculate XP needed for a specific level"""
        return ((level - 1) ** 2) * 100

    async def add_xp(self, user_id: str, xp_amount: int = 10):
        """Add XP to user with cooldown"""
        try:
            current_time = datetime.now()
            if user_id in self.xp_cooldown:
                if (current_time - self.xp_cooldown[user_id]).total_seconds() < 60:
                    return

            self.xp_cooldown[user_id] = current_time
            cursor = self.db.cursor()

            # Get current XP and level
            cursor.execute('SELECT xp, level FROM user_xp WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()

            if result:
                current_xp, current_level = result
                new_xp = current_xp + xp_amount
            else:
                current_xp, current_level = 0, 1
                new_xp = xp_amount
                cursor.execute('INSERT INTO user_xp (user_id, xp, level) VALUES (?, ?, ?)',
                             (user_id, new_xp, current_level))

            new_level = self.calculate_level(new_xp)

            # Update database
            cursor.execute('''
                UPDATE user_xp 
                SET xp = ?, level = ?, last_xp_gain = CURRENT_TIMESTAMP 
                WHERE user_id = ?
            ''', (new_xp, new_level, user_id))

            self.db.commit()

            # Handle level up
            if new_level > current_level:
                for guild in self.bot.guilds:
                    member = guild.get_member(int(user_id))
                    if member:
                        embed = discord.Embed(
                            title="🎉 Level Up!",
                            description=f"Congratulations {member.mention}! You've reached level {new_level}!",
                            color=discord.Color.gold()
                        )
                        # Send level up message to the first available channel
                        for channel in guild.text_channels:
                            try:
                                await channel.send(embed=embed)
                                break
                            except discord.Forbidden:
                                continue

        except Exception as e:
            self.logger.error(f"Error adding XP: {str(e)}")

    async def award_achievement(self, user_id: str, achievement_id: str, guild: discord.Guild = None):
        """Award an achievement to a user in a specific guild"""
        try:
            self.logger.info(f"Attempting to award achievement {achievement_id} to user {user_id} in guild {guild.name if guild else 'None'}")

            if user_id not in self.user_achievements:
                self.user_achievements[user_id] = []

            if achievement_id not in self.user_achievements[user_id]:
                achievement = self.achievements[achievement_id]
                self.user_achievements[user_id].append(achievement_id)
                self.save_achievements()

                user = self.bot.get_user(int(user_id))
                if user and guild:
                    # Award role in the specific guild
                    if achievement.role_name:
                        try:
                            member = guild.get_member(int(user_id))
                            self.logger.info(f"Found member {member.name} ({member.id}) in guild {guild.name}")

                            role = discord.utils.get(guild.roles, name=achievement.role_name)
                            if role:
                                self.logger.info(f"Found role {role.name} (Position: {role.position}) in guild {guild.name}")

                                if guild.me.guild_permissions.manage_roles:
                                    self.logger.info(f"Bot has manage_roles permission in {guild.name}")

                                    if guild.me.top_role > role:
                                        self.logger.info(f"Bot's role ({guild.me.top_role.name}, pos: {guild.me.top_role.position}) is higher than {role.name} (pos: {role.position})")
                                        await member.add_roles(role, reason=f"Earned achievement: {achievement.name}")
                                        self.logger.info(f"✅ Successfully awarded role {role.name} to {member.name} in {guild.name}")
                                    else:
                                        self.logger.warning(f"❌ Bot's role is not high enough to assign {role.name} in {guild.name}")
                                else:
                                    self.logger.warning(f"❌ Bot lacks permission to manage roles in {guild.name}")
                            else:
                                self.logger.warning(f"Role {achievement.role_name} not found in {guild.name}, attempting to create")
                                await self.setup_achievement_roles(guild)
                                role = discord.utils.get(guild.roles, name=achievement.role_name)
                                if role:
                                    await member.add_roles(role, reason=f"Earned achievement: {achievement.name}")
                                    self.logger.info(f"✅ Successfully awarded role {role.name} to {member.name} after creation")
                                else:
                                    self.logger.error(f"❌ Failed to create role {achievement.role_name} in {guild.name}")
                        except Exception as e:
                            self.logger.error(f"Error assigning role in {guild.name}: {str(e)}", exc_info=True)

                    # Send achievement notification
                    embed = discord.Embed(
                        title=f"🎉 Achievement Unlocked!",
                        description=(
                            f"{achievement.emoji} **{achievement.name}**\n"
                            f"{achievement.description}\n"
                            f"*+{achievement.points} points*"
                        ),
                        color=discord.Color.gold()
                    )

                    if achievement.role_name:
                        embed.add_field(
                            name="🏆 Role Awarded",
                            value=f"You've been awarded the `{achievement.role_name}` role!",
                            inline=False
                        )

                    try:
                        await user.send(embed=embed)
                    except discord.Forbidden:
                        pass  # User has DMs disabled

                self.logger.info(f"Finished processing achievement {achievement_id} for user {user_id}")
                return True

        except Exception as e:
            self.logger.error(f"Error awarding achievement: {str(e)}", exc_info=True)
        return False

    def load_achievements(self):
        """Load saved user achievements from file"""
        try:
            if os.path.exists('data/achievements.json'):
                with open('data/achievements.json', 'r') as f:
                    self.user_achievements = json.load(f)
            self.logger.info("Successfully loaded user achievements")
        except Exception as e:
            self.logger.error(f"Error loading achievements: {str(e)}")

    def save_achievements(self):
        """Save user achievements to file"""
        try:
            os.makedirs('data', exist_ok=True)
            with open('data/achievements.json', 'w') as f:
                json.dump(self.user_achievements, f)
            self.logger.info("Successfully saved user achievements")
        except Exception as e:
            self.logger.error(f"Error saving achievements: {str(e)}")

    async def setup_achievement_roles(self, guild: discord.Guild):
        """Create achievement roles if they don't exist"""
        try:
            self.logger.info(f"Setting up achievement roles for guild: {guild.name}")
            existing_roles = {role.name: role for role in guild.roles}

            # Check bot permissions first
            if not guild.me.guild_permissions.manage_roles:
                self.logger.error(f"Bot lacks 'Manage Roles' permission in guild: {guild.name}")
                return

            self.logger.info(f"Bot has required permissions in {guild.name}")

            # Calculate position below bot's role
            target_position = guild.me.top_role.position - 1

            for achievement in self.achievements.values():
                if achievement.role_name and achievement.role_name not in existing_roles:
                    try:
                        # Create role with a color based on points
                        color = discord.Color.from_rgb(
                            min(achievement.points * 2, 255),  # More points = more red
                            max(255 - achievement.points, 0),  # More points = less green
                            255  # Constant blue for consistency
                        )
                        role = await guild.create_role(
                            name=achievement.role_name,
                            color=color,
                            reason="Achievement role",
                            hoist=True  # Show role separately in member list
                        )
                        self.logger.info(f"Successfully created role {role.name} in {guild.name}")

                        # Immediately move role to correct position
                        try:
                            await role.edit(position=target_position)
                            self.logger.info(f"Successfully positioned role {role.name} at position {target_position}")
                        except discord.Forbidden:
                            self.logger.warning(f"Could not move role {role.name} in hierarchy - insufficient permissions")
                        except Exception as e:
                            self.logger.error(f"Error positioning role {role.name}: {str(e)}")

                    except discord.Forbidden:
                        self.logger.error(f"Failed to create role {achievement.role_name} - insufficient permissions")
                    except Exception as e:
                        self.logger.error(f"Error creating role {achievement.role_name}: {str(e)}")
                else:
                    # Update existing role position if needed
                    role = existing_roles[achievement.role_name]
                    if role.position < target_position:
                        try:
                            await role.edit(position=target_position)
                            self.logger.info(f"Updated position for existing role {role.name} to {target_position}")
                        except Exception as e:
                            self.logger.error(f"Error updating position for role {role.name}: {str(e)}")

        except Exception as e:
            self.logger.error(f"Error setting up achievement roles: {str(e)}", exc_info=True)

    @commands.command(name="achievements")
    async def view_achievements(self, ctx):
        """View your earned achievements"""
        try:
            user_id = str(ctx.author.id)
            earned = self.user_achievements.get(user_id, [])
            total_points = sum(self.achievements[a].points for a in earned)

            embed = discord.Embed(
                title="🏆 Your Achievements",
                description=f"You've earned {len(earned)} achievements and {total_points} points!",
                color=discord.Color.blue()
            )

            # Earned Achievements
            earned_text = ""
            for achievement_id in earned:
                achievement = self.achievements[achievement_id]
                earned_text += f"{achievement.emoji} **{achievement.name}** (+{achievement.points})\n"
                earned_text += f"➜ {achievement.description}\n\n"

            if earned_text:
                embed.add_field(
                    name="🌟 Earned Achievements",
                    value=earned_text,
                    inline=False
                )

            # Available Achievements (excluding secret ones)
            available = [a for a in self.achievements.values()
                        if not a.secret and a.id not in earned]
            if available:
                available_text = ""
                for achievement in available:
                    available_text += f"{achievement.emoji} **{achievement.name}**\n"
                    available_text += f"➜ {achievement.description}\n\n"

                embed.add_field(
                    name="📝 Available Achievements",
                    value=available_text,
                    inline=False
                )

            embed.set_footer(text="Keep interacting to unlock more achievements!")
            await ctx.send(embed=embed)
            self.logger.info(f"Displayed achievements for user {ctx.author.name}")

        except Exception as e:
            self.logger.error(f"Error displaying achievements: {str(e)}")
            await ctx.send("❌ An error occurred while fetching achievements.")

    @commands.command(name='level')
    async def show_level(self, ctx, member: discord.Member = None):
        """Show user's current level and XP progress"""
        try:
            target = member or ctx.author
            cursor = self.db.cursor()
            cursor.execute('SELECT xp, level FROM user_xp WHERE user_id = ?', (str(target.id),))
            result = cursor.fetchone()

            if result:
                xp, level = result
                next_level_xp = self.calculate_xp_for_level(level + 1)
                current_level_xp = self.calculate_xp_for_level(level)
                progress = ((xp - current_level_xp) / (next_level_xp - current_level_xp)) * 10
                progress_bar = '█' * int(progress) + '░' * (10 - int(progress))

                embed = discord.Embed(
                    title=f"Level Status for {target.display_name}",
                    color=discord.Color.blue()
                )
                embed.add_field(
                    name="Current Level",
                    value=f"```Level {level}```",
                    inline=False
                )
                embed.add_field(
                    name="Experience",
                    value=f"```{xp}/{next_level_xp} XP\n{progress_bar}```",
                    inline=False
                )
                await ctx.send(embed=embed)
            else:
                await ctx.send(f"{target.mention} hasn't earned any XP yet!")

        except Exception as e:
            self.logger.error(f"Error showing level: {str(e)}")
            await ctx.send("❌ An error occurred while fetching level information.")

    @commands.command(name='leaderboard')
    async def show_leaderboard(self, ctx):
        """Show XP leaderboard"""
        try:
            cursor = self.db.cursor()
            cursor.execute('''
                SELECT user_id, xp, level 
                FROM user_xp 
                ORDER BY xp DESC 
                LIMIT 10
            ''')
            results = cursor.fetchall()

            if results:
                embed = discord.Embed(
                    title="🏆 XP Leaderboard",
                    color=discord.Color.gold()
                )

                leaderboard_text = ""
                for i, (user_id, xp, level) in enumerate(results, 1):
                    member = ctx.guild.get_member(int(user_id))
                    name = member.display_name if member else "Unknown User"
                    leaderboard_text += f"{i}. {name} - Level {level} ({xp} XP)\n"

                embed.description = f"```{leaderboard_text}```"
                await ctx.send(embed=embed)
            else:
                await ctx.send("No XP data available yet!")

        except Exception as e:
            self.logger.error(f"Error showing leaderboard: {str(e)}")
            await ctx.send("❌ An error occurred while fetching the leaderboard.")


    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        """Create achievement roles when bot joins a new guild"""
        await self.setup_achievement_roles(guild)

    @commands.Cog.listener()
    async def on_message(self, message):
        """Listen for messages to track achievements and XP"""
        if message.author.bot:
            return

        user_id = str(message.author.id)
        try:
            # Add XP for message
            await self.add_xp(user_id)

            # Track achievements as before
            if message.content.startswith('!ask') or message.content.startswith('!chat'):
                await self.award_achievement(user_id, "ai_explorer", message.guild)

            # Track night owl achievement
            current_hour = datetime.now().hour
            if current_hour >= 0 and current_hour < 6:
                if message.content.startswith('!11') or message.content.startswith('!12'):
                    await self.award_achievement(user_id, "night_owl", message.guild)

        except Exception as e:
            self.logger.error(f"Error in achievement/XP listener: {str(e)}")

    @commands.command(name='checkroles')
    @commands.has_permissions(administrator=True)
    async def check_roles(self, ctx):
        """Debug command to check bot permissions and role setup"""
        try:
            embed = discord.Embed(
                title="🔍 Role System Status",
                color=discord.Color.blue()
            )

            # Check bot permissions
            perms = ctx.guild.me.guild_permissions
            bot_perms = (
                f"✅ Manage Roles: {perms.manage_roles}\n"
                f"✅ Bot's Top Role: {ctx.guild.me.top_role.name}\n"
                f"✅ Bot's Role Position: {ctx.guild.me.top_role.position}"
            )
            embed.add_field(
                name="Bot Permissions",
                value=f"```{bot_perms}```",
                inline=False
            )

            # List achievement roles
            achievement_roles = []
            for achievement in self.achievements.values():
                if achievement.role_name:
                    role = discord.utils.get(ctx.guild.roles, name=achievement.role_name)
                    status = "✅ Created" if role else "❌ Missing"
                    pos = role.position if role else "N/A"
                    achievement_roles.append(f"{achievement.role_name}: {status} (Position: {pos})")

            embed.add_field(
                name="Achievement Roles",
                value="```" + "\n".join(achievement_roles) + "```",
                inline=False
            )

            await ctx.send(embed=embed)

            # Try to fix any missing roles
            await self.setup_achievement_roles(ctx.guild)
            self.logger.info(f"Role system check completed in guild: {ctx.guild.name}")

        except Exception as e:
            self.logger.error(f"Error checking roles: {str(e)}", exc_info=True)
            await ctx.send("❌ An error occurred while checking roles.")


async def setup(bot):
    achievements_cog = Achievements(bot)
    await bot.add_cog(achievements_cog)
    # Setup roles in all current guilds
    for guild in bot.guilds:
        await achievements_cog.setup_achievement_roles(guild)
    logging.getLogger('discord_bot').info("Achievements cog loaded successfully")