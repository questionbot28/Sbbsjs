import discord
from discord.ext import commands
import logging
from typing import Dict, List, Set
import json
import os
from datetime import datetime
import sqlite3
import asyncio
import os
from utils.badge_generator import AchievementBadgeGenerator

class Achievement:
    def __init__(self, id: str, name: str, description: str, emoji: str, points: int, role_name: str = None, secret: bool = False, required_count: int = None):
        self.id = id
        self.name = name
        self.description = description
        self.emoji = emoji
        self.points = points
        self.role_name = role_name
        self.secret = secret
        self.required_count = required_count  # Number required to complete achievement

class Achievements(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger('discord_bot')
        self.xp_cooldown = {}
        self.setup_database()
        # Ensure static directories exist
        os.makedirs('static/css', exist_ok=True)
        os.makedirs('static/badges', exist_ok=True)
        self.achievements = {
            "first_question": Achievement(
                "first_question",
                "Curious Mind",
                "Ask your first practice question",
                "🎯",
                10,
                "Curious Mind",
                required_count=1
            ),
            "knowledge_seeker": Achievement(
                "knowledge_seeker", 
                "Knowledge Seeker",
                "Use practice questions from 5 different subjects",
                "📚",
                50,
                "Knowledge Seeker",
                required_count=5
            ),
            "master_student": Achievement(
                "master_student",
                "Master Student", 
                "Complete 100 practice questions",
                "🎓",
                100,
                "Master Student",
                required_count=100
            ),
            # Subject specific achievements
            "physics_enthusiast": Achievement(
                "physics_enthusiast",
                "Physics Enthusiast",
                "Complete 25 physics questions",
                "⚡",
                40,
                "Physics Expert",
                required_count=25
            ),
            "math_wizard": Achievement(
                "math_wizard",
                "Math Wizard",
                "Complete 25 mathematics questions",
                "🔢",
                40,
                "Math Expert",
                required_count=25
            ),
            "chemistry_expert": Achievement(
                "chemistry_expert",
                "Chemistry Expert",
                "Complete 25 chemistry questions",
                "🧪",
                40,
                "Chemistry Expert",
                required_count=25
            ),
            "biology_scholar": Achievement(
                "biology_scholar",
                "Biology Scholar",
                "Complete 25 biology questions",
                "🧬",
                40,
                "Biology Expert",
                required_count=25
            ),
            # Study Habits
            "daily_scholar": Achievement(
                "daily_scholar",
                "Daily Scholar",
                "Study for 7 consecutive days",
                "📅",
                30,
                "Daily Scholar",
                required_count=7
            ),
            "weekend_warrior": Achievement(
                "weekend_warrior",
                "Weekend Warrior",
                "Study on both Saturday and Sunday",
                "🎯",
                25,
                "Weekend Warrior",
                required_count=2
            ),
            # Music achievements
            "music_lover": Achievement(
                "music_lover",
                "Music Enthusiast",
                "Play your first song",
                "🎵",
                10,
                "Music Enthusiast",
                required_count=1
            ),
            "playlist_master": Achievement(
                "playlist_master",
                "Playlist Master",
                "Create a queue with 10 songs",
                "🎶",
                30,
                "Playlist Master",
                required_count=10
            ),
            "music_explorer": Achievement(
                "music_explorer",
                "Music Explorer",
                "Listen to songs from 5 different genres",
                "🎧",
                35,
                "Music Explorer",
                required_count=5
            ),
            "rhythm_master": Achievement(
                "rhythm_master",
                "Rhythm Master",
                "Play 50 different songs",
                "🎼",
                45,
                "Rhythm Master",
                required_count=50
            ),
            # AI Interaction achievements
            "ai_explorer": Achievement(
                "ai_explorer",
                "AI Explorer",
                "Have your first AI conversation",
                "🤖",
                20,
                "AI Explorer",
                required_count=1
            ),
            "deep_thinker": Achievement(
                "deep_thinker",
                "Deep Thinker",
                "Ask 50 questions to AI",
                "🧠",
                75,
                "Deep Thinker",
                required_count=50
            ),
            "ai_enthusiast": Achievement(
                "ai_enthusiast",
                "AI Enthusiast",
                "Have meaningful conversations with AI for 30 minutes",
                "💡",
                40,
                "AI Enthusiast",
                required_count=30
            ),
            "creative_mind": Achievement(
                "creative_mind",
                "Creative Mind",
                "Generate unique study materials using AI",
                "🎨",
                35,
                "Creative Mind",
                required_count=1
            ),
            # Community achievements
            "helpful_peer": Achievement(
                "helpful_peer",
                "Helpful Peer",
                "Help others with their questions",
                "🤝",
                30,
                "Helpful Peer",
                required_count=1
            ),
            "community_builder": Achievement(
                "community_builder",
                "Community Builder",
                "Invite 5 new members to the server",
                "🌟",
                50,
                "Community Builder",
                required_count=5
            ),
            # Secret achievements
            "night_owl": Achievement(
                "night_owl",
                "Night Owl",
                "Study after midnight",
                "🦉",
                25,
                "Night Owl",
                True,
                required_count=1
            ),
            "speed_learner": Achievement(
                "speed_learner",
                "Speed Learner",
                "Complete 5 questions in under 5 minutes",
                "⚡",
                50,
                "Speed Learner",
                True,
                required_count=5
            ),
            "early_bird": Achievement(
                "early_bird",
                "Early Bird",
                "Study before 6 AM",
                "🌅",
                30,
                "Early Bird",
                True,
                required_count=1
            ),
            "marathon_learner": Achievement(
                "marathon_learner",
                "Marathon Learner",
                "Study for more than 3 hours continuously",
                "🏃",
                60,
                "Marathon Learner",
                True,
                required_count=3
            )
        }
        self.user_achievements = {}
        self.load_achievements()
        self.badge_generator = AchievementBadgeGenerator()
        self.setup_badges()
        self.logger.info("Achievements system initialized")

    def setup_database(self):
        """Initialize SQLite database for XP and achievement progress"""
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

            # Create achievement progress table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS achievement_progress (
                    user_id TEXT,
                    achievement_id TEXT,
                    current_count INTEGER DEFAULT 0,
                    completed BOOLEAN DEFAULT 0,
                    completion_date TIMESTAMP,
                    PRIMARY KEY (user_id, achievement_id)
                )
            ''')

            self.db.commit()
            self.logger.info("Database initialized successfully")
        except Exception as e:
            self.logger.error(f"Error setting up database: {str(e)}")

    async def get_achievement_progress(self, user_id: str, achievement_id: str) -> tuple:
        """Get current progress for an achievement"""
        cursor = self.db.cursor()
        cursor.execute(
            'SELECT current_count, completed FROM achievement_progress WHERE user_id = ? AND achievement_id = ?',
            (user_id, achievement_id)
        )
        result = cursor.fetchone()
        if result:
            return result[0], bool(result[1])
        return 0, False

    async def update_achievement_progress(self, user_id: str, achievement_id: str, guild: discord.Guild = None, count: int = 1):
        """Update progress towards an achievement"""
        try:
            achievement = self.achievements[achievement_id]
            current_count, completed = await self.get_achievement_progress(user_id, achievement_id)

            if not completed:
                new_count = current_count + count
                cursor = self.db.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO achievement_progress 
                    (user_id, achievement_id, current_count, completed, completion_date)
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (user_id, achievement_id, new_count, new_count >= achievement.required_count))
                self.db.commit()

                # Check if achievement is now completed
                if new_count >= achievement.required_count and not completed:
                    await self.award_achievement(user_id, achievement_id, guild)

        except Exception as e:
            self.logger.error(f"Error updating achievement progress: {str(e)}")

    def generate_progress_bar(self, current: int, required: int, length: int = 10) -> str:
        """Generate a text-based progress bar"""
        filled = int((current / required) * length)
        return '█' * filled + '░' * (length - filled)

    def setup_badges(self):
        """Generate and save achievement badges"""
        if not os.path.exists('static/badges'):
            os.makedirs('static/badges')

        for achievement_id, achievement in self.achievements.items():
            badge_svg = self.badge_generator.generate_badge(
                emoji=achievement.emoji,
                color="#4CAF50" if not achievement.secret else "#9C27B0"
            )
            self.badge_generator.save_badge(badge_svg, f"achievement_{achievement_id}")

    @commands.command(name="achievements")
    async def view_achievements(self, ctx, member: discord.Member = None):
        """View achievements with animated badges"""
        try:
            target = member or ctx.author
            user_id = str(target.id)

            embed = discord.Embed(
                title=f"🏆 Achievements - {target.display_name}",
                color=discord.Color.blue()
            )

            # Track total points
            total_points = 0
            unlocked_count = 0

            # Group achievements by category
            categories = {
                "📚 Education": [],
                "⏰ Study Habits": [],
                "🎵 Music": [],
                "🤖 AI": [],
                "🌟 Community": []
            }

            for achievement_id, achievement in self.achievements.items():
                if achievement.secret and achievement_id not in self.user_achievements.get(user_id, []):
                    continue

                current_count, completed = await self.get_achievement_progress(user_id, achievement_id)

                if completed:
                    total_points += achievement.points
                    unlocked_count += 1

                # Create progress display
                if achievement.required_count:
                    progress_bar = self.generate_progress_bar(
                        min(current_count, achievement.required_count),
                        achievement.required_count
                    )
                    progress_text = f"{min(current_count, achievement.required_count)}/{achievement.required_count}"
                else:
                    progress_bar = ""
                    progress_text = ""

                # Format achievement text with sparkle emoji for completed achievements
                status = f"✨ {achievement.emoji}" if completed else "🔄"
                achievement_text = (
                    f"{status} **{achievement.name}** (+{achievement.points})\n"
                    f"➜ {achievement.description}\n"
                )
                if progress_bar and not completed:
                    achievement_text += f"```{progress_bar} {progress_text}```\n"

                # Add to appropriate category
                if "question" in achievement_id or any(subj in achievement_id for subj in ["physics", "math", "chemistry", "biology"]):
                    categories["📚 Education"].append(achievement_text)
                elif "daily" in achievement_id or "streak" in achievement_id or "weekend" in achievement_id:
                    categories["⏰ Study Habits"].append(achievement_text)
                elif "music" in achievement_id or "song" in achievement_id:
                    categories["🎵 Music"].append(achievement_text)
                elif "ai" in achievement_id:
                    categories["🤖 AI"].append(achievement_text)
                else:
                    categories["🌟 Community"].append(achievement_text)

            # Add summary with sparkle emojis
            embed.description = f"✨ Unlocked {unlocked_count} achievements and earned {total_points} points! ✨"

            # Add each category to embed
            for category, achievements in categories.items():
                if achievements:
                    embed.add_field(
                        name=f"{category}",
                        value="\n".join(achievements),
                        inline=False
                    )

            embed.set_footer(text="✨ Keep interacting to unlock more achievements! ✨")
            await ctx.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Error displaying achievements: {str(e)}")
            await ctx.send("❌ An error occurred while fetching achievements.")

    async def award_achievement(self, user_id: str, achievement_id: str, guild: discord.Guild = None):
        """Award an achievement to a user in a specific guild"""
        try:
            if user_id not in self.user_achievements:
                self.user_achievements[user_id] = []

            if achievement_id not in self.user_achievements[user_id]:
                achievement = self.achievements[achievement_id]
                self.user_achievements[user_id].append(achievement_id)
                self.save_achievements()

                # Create congratulatory message with sparkle effects
                embed = discord.Embed(
                    title=f"✨ Achievement Unlocked! ✨",
                    description=(
                        f"{achievement.emoji} **{achievement.name}**\n"
                        f"{achievement.description}\n"
                        f"*+{achievement.points} points*"
                    ),
                    color=discord.Color.gold()
                )

                # Add role notification if applicable
                if achievement.role_name:
                    embed.add_field(
                        name="🏆 Role Awarded",
                        value=f"You've been awarded the `{achievement.role_name}` role!",
                        inline=False
                    )

                # Try to send DM
                user = self.bot.get_user(int(user_id))
                if user:
                    try:
                        await user.send(embed=embed)
                    except discord.Forbidden:
                        pass  # User has DMs disabled

                # Award role if in a guild
                if guild and achievement.role_name:
                    await self.award_achievement_role(guild, int(user_id), achievement.role_name)

                return True

        except Exception as e:
            self.logger.error(f"Error awarding achievement: {str(e)}")
        return False

    async def award_achievement_role(self, guild: discord.Guild, user_id: int, role_name: str):
        try:
            member = guild.get_member(user_id)
            if member:
                role = discord.utils.get(guild.roles, name=role_name)
                if role and guild.me.guild_permissions.manage_roles and guild.me.top_role > role:
                    await member.add_roles(role, reason=f"Earned achievement")
                else:
                    self.logger.warning(f"Could not award role {role_name}. Check bot permissions or role existence.")
        except Exception as e:
            self.logger.error(f"Error awarding achievement role: {str(e)}")


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

        except Exception as e:
            self.logger.error(f"Error checking roles: {str(e)}")
            await ctx.send("❌ An error occurred while checking roles.")

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

            # Track AI interactions
            if message.content.startswith('!ask') or message.content.startswith('!chat'):
                await self.update_achievement_progress(user_id, "ai_explorer", message.guild)
                if not hasattr(self, 'ai_interactions'):
                    self.ai_interactions = {}
                if user_id not in self.ai_interactions:
                    self.ai_interactions[user_id] = 0
                self.ai_interactions[user_id] += 1
                if self.ai_interactions[user_id] >= 50:
                    await self.update_achievement_progress(user_id, "deep_thinker", message.guild)

            # Track subject-specific achievements
            if message.content.startswith('!11') or message.content.startswith('!12'):
                subject = message.content.split()[1].lower() if len(message.content.split()) > 1 else None
                if subject:
                    if not hasattr(self, 'subject_counts'):
                        self.subject_counts = {}
                    if user_id not in self.subject_counts:
                        self.subject_counts[user_id] = {'physics': 0, 'mathematics': 0, 'chemistry': 0, 'biology': 0}

                    subject_mapping = {
                        'physics': 'physics',
                        'maths': 'mathematics',
                        'math': 'mathematics',
                        'chemistry': 'chemistry',
                        'biology': 'biology',
                        'bio': 'biology'
                    }

                    norm_subject = subject_mapping.get(subject)
                    if norm_subject in self.subject_counts[user_id]:
                        self.subject_counts[user_id][norm_subject] += 1
                        await self.update_achievement_progress(user_id, f"{norm_subject}_enthusiast", message.guild)

            # Track time-based achievements
            current_hour = datetime.now().hour
            if message.content.startswith('!11') or message.content.startswith('!12'):
                if current_hour < 6:
                    await self.update_achievement_progress(user_id, "early_bird", message.guild)
                elif current_hour >= 0 and current_hour < 6:
                    await self.update_achievement_progress(user_id, "night_owl", message.guild)

            # Track study streaks
            current_date = datetime.now().date()
            if not hasattr(self, 'study_dates'):
                self.study_dates = {}
            if user_id not in self.study_dates:
                self.study_dates[user_id] = set()

            self.study_dates[user_id].add(current_date)

            # Check for daily scholar
            dates = sorted(self.study_dates[user_id])
            if len(dates) >= 7:
                consecutive_days = 1
                for i in range(1, len(dates)):
                    if (dates[i] - dates[i-1]).days == 1:
                        consecutive_days += 1
                        if consecutive_days >= 7:
                            await self.update_achievement_progress(user_id, "daily_scholar", message.guild)
                            break
                    else:
                        consecutive_days = 1

            # Check for weekend warrior
            if current_date.weekday() >= 5:  # Saturday or Sunday
                weekend_dates = {d for d in self.study_dates[user_id] if d.weekday() >= 5}
                if len(weekend_dates) >= 2:
                    await self.update_achievement_progress(user_id, "weekend_warrior", message.guild)

        except Exception as e:
            self.logger.error(f"Error in achievement/XP listener: {str(e)}")

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

                embed.description = f"```\n{leaderboard_text}```"
                await ctx.send(embed=embed)
            else:
                await ctx.send("No XP data available yet!")

        except Exception as e:
            self.logger.error(f"Error showing leaderboard: {str(e)}")
            await ctx.send("❌ Anerror occurred while fetching the leaderboard.")


async def setup(bot):
    await bot.add_cog(Achievements(bot))