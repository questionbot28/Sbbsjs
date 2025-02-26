import discord
from discord.ext import commands
import sqlite3
import logging
import asyncio
import json
from datetime import datetime, timedelta
import google.generativeai as genai
import os
from typing import List, Dict, Optional

class LearningAssistant(commands.Cog):
    """A cog for AI-powered learning assistance features"""

    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger('discord_bot')
        # Configure Gemini
        if not os.getenv('GOOGLE_API_KEY'):
            self.logger.error("Google API key not found in environment variables")
        else:
            try:
                genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
                self.logger.info("Successfully configured Gemini API")
                self.model = genai.GenerativeModel('gemini-2.0-flash')
                self.logger.info("Successfully initialized Gemini model")
            except Exception as e:
                self.logger.error(f"Failed to configure Gemini: {str(e)}")
        self.setup_database()

    def setup_database(self):
        """Initialize SQLite database for learning assistant features"""
        try:
            self.db = sqlite3.connect('data/user_data.db')
            cursor = self.db.cursor()

            # Create study_progress table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS study_progress (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    subject TEXT NOT NULL,
                    topic TEXT NOT NULL,
                    correct_answers INTEGER DEFAULT 0,
                    total_attempts INTEGER DEFAULT 0,
                    last_study_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Create study_schedule table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS study_schedule (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    subject TEXT NOT NULL,
                    start_date DATE NOT NULL,
                    end_date DATE NOT NULL,
                    daily_topics TEXT NOT NULL,
                    completed_topics TEXT DEFAULT '[]',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Create study_tip_categories table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS study_tip_categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    category_name TEXT NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, category_name)
                )
            ''')

            # Create study_tips table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS study_tips (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category_id INTEGER NOT NULL,
                    user_id TEXT NOT NULL,
                    tip_content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(category_id) REFERENCES study_tip_categories(id)
                )
            ''')

            self.db.commit()
            self.logger.info("Learning assistant database initialized")
        except Exception as e:
            self.logger.error(f"Error setting up learning assistant database: {str(e)}")

    @commands.group(name='learn', invoke_without_command=True)
    async def learn(self, ctx):
        """Learning assistant command group"""
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                title="📚 Learning Assistant Commands",
                description="Here's how I can help you learn:",
                color=discord.Color.blue()
            )
            embed.add_field(
                name="Smart Questions",
                value="```\n!learn quiz <subject> - Get personalized practice questions\n```",
                inline=False
            )
            embed.add_field(
                name="Study Schedule",
                value="```\n!learn schedule <subject> <days> - Create a study plan\n!learn progress - Check your study progress\n```",
                inline=False
            )
            embed.add_field(
                name="Homework Help",
                value="```\n!learn solve <question> - Get step-by-step solutions\n```",
                inline=False
            )
            embed.add_field(
                name="Study Tips",
                value="```\nUse the !tips command to manage your study tips.\n```",
                inline=False
            )
            await ctx.send(embed=embed)

    @learn.command(name='quiz')
    async def generate_quiz(self, ctx, subject: str):
        """Generate a personalized quiz based on user's weak areas"""
        try:
            # Get user's study progress
            cursor = self.db.cursor()
            cursor.execute('''
                SELECT topic, correct_answers, total_attempts 
                FROM study_progress 
                WHERE user_id = ? AND subject = ?
                ORDER BY (CAST(correct_answers AS FLOAT) / total_attempts) ASC
                LIMIT 1
            ''', (str(ctx.author.id), subject))

            weak_topic = cursor.fetchone()

            # Generate question prompt
            if weak_topic and weak_topic[1] > 0:
                topic = weak_topic[0]
                accuracy = weak_topic[1] / weak_topic[2]
                prompt = f"Generate a {subject} question about {topic}. The student has an accuracy of {accuracy:.2%} on this topic. Make it slightly challenging but not too difficult."
            else:
                prompt = f"Generate an introductory {subject} question suitable for a beginner."

            # Send initial response
            msg = await ctx.send("🤔 Generating your personalized question...")

            try:
                response = await asyncio.to_thread(self.model.generate_content, prompt)

                question = response.text.strip()

                embed = discord.Embed(
                    title=f"📝 {subject} Question",
                    description=question,
                    color=discord.Color.green()
                )
                embed.set_footer(text="Take your time to think about it! Use !learn solve to get help if needed.")

                await msg.edit(content=None, embed=embed)

            except Exception as e:
                self.logger.error(f"Error generating question: {str(e)}")
                await msg.edit(content="❌ Sorry, I couldn't generate a question right now. Please try again later.")

        except Exception as e:
            self.logger.error(f"Error in quiz command: {str(e)}")
            await ctx.send("❌ An error occurred while generating your quiz.")

    @learn.command(name='schedule')
    async def create_schedule(self, ctx, subject: str, days: int):
        """Create a personalized study schedule"""
        if days <= 0 or days > 365:
            await ctx.send("❌ Please choose a number of days between 1 and 365.")
            return

        try:
            msg = await ctx.send("📅 Creating your study schedule...")

            try:
                # Generate study plan using Gemini
                prompt = f"""Create a {days}-day study plan for {subject}. 
                Format the response as a JSON array of daily topics. 
                Each topic should be specific and achievable in one study session.
                Example format: ["Introduction to {subject}", "Basic Concepts", ...]"""

                response = await asyncio.to_thread(self.model.generate_content, prompt)

                # Parse the study plan
                try:
                    daily_topics = json.loads(response.text.strip())
                except:
                    # If JSON parsing fails, split by newlines as fallback
                    daily_topics = [topic.strip() for topic in response.text.split('\n') if topic.strip()]

                # Save to database
                cursor = self.db.cursor()
                start_date = datetime.now().date()
                end_date = start_date + timedelta(days=days)

                cursor.execute('''
                    INSERT INTO study_schedule (user_id, subject, start_date, end_date, daily_topics)
                    VALUES (?, ?, ?, ?, ?)
                ''', (str(ctx.author.id), subject, start_date, end_date, json.dumps(daily_topics)))

                self.db.commit()

                # Create embed with schedule
                embed = discord.Embed(
                    title=f"📚 Your {subject} Study Schedule",
                    description=f"Here's your {days}-day study plan:",
                    color=discord.Color.blue()
                )

                # Add first 5 days to embed
                for i, topic in enumerate(daily_topics[:5], 1):
                    date = start_date + timedelta(days=i-1)
                    embed.add_field(
                        name=f"Day {i} ({date.strftime('%Y-%m-%d')})",
                        value=topic,
                        inline=False
                    )

                if len(daily_topics) > 5:
                    embed.add_field(
                        name="...",
                        value=f"*{len(daily_topics) - 5} more days planned*",
                        inline=False
                    )

                embed.set_footer(text="Use !learn progress to track your progress")
                await msg.edit(content=None, embed=embed)

            except Exception as e:
                self.logger.error(f"Error creating schedule: {str(e)}")
                await msg.edit(content="❌ Sorry, I couldn't create your schedule right now. Please try again later.")

        except Exception as e:
            self.logger.error(f"Error in schedule command: {str(e)}")
            await ctx.send("❌ An error occurred while creating your schedule.")

    @learn.command(name='solve')
    async def solve_problem(self, ctx, *, question: str):
        """Provide step-by-step solution to a problem"""
        try:
            msg = await ctx.send("🤔 Analyzing your question...")

            try:
                prompt = f"""Solve this problem step by step:
                Question: {question}

                Format your response with:
                1. First identify the type of problem
                2. List any key information or given values
                3. Provide a clear step-by-step solution
                4. Explain each step
                5. Give the final answer"""

                response = await asyncio.to_thread(self.model.generate_content, prompt)

                solution = response.text.strip()

                # Create embed with solution
                embed = discord.Embed(
                    title="📝 Problem Solution",
                    description=f"**Question:**\n{question}\n\n**Solution:**\n{solution}",
                    color=discord.Color.green()
                )

                await msg.edit(content=None, embed=embed)

            except Exception as e:
                self.logger.error(f"Error generating solution: {str(e)}")
                await msg.edit(content="❌ Sorry, I couldn't solve this problem right now. Please try again later.")

        except Exception as e:
            self.logger.error(f"Error in solve command: {str(e)}")
            await ctx.send("❌ An error occurred while solving your problem.")

    @learn.command(name='progress')
    async def check_progress(self, ctx):
        """Check study progress and schedule"""
        try:
            cursor = self.db.cursor()

            # Get active study schedules
            cursor.execute('''
                SELECT subject, start_date, end_date, daily_topics, completed_topics
                FROM study_schedule
                WHERE user_id = ? AND end_date >= date('now')
                ORDER BY start_date ASC
            ''', (str(ctx.author.id),))

            schedules = cursor.fetchall()

            if not schedules:
                await ctx.send("You don't have any active study schedules. Use `!learn schedule` to create one!")
                return

            # Create embed with progress
            embed = discord.Embed(
                title="📊 Your Study Progress",
                description="Here's how you're doing:",
                color=discord.Color.blue()
            )

            for subject, start_date, end_date, daily_topics, completed_topics in schedules:
                try:
                    daily_topics = json.loads(daily_topics)
                    completed = json.loads(completed_topics) if completed_topics else []

                    progress = len(completed) / len(daily_topics) * 100
                    days_left = (datetime.strptime(end_date, '%Y-%m-%d').date() - datetime.now().date()).days

                    embed.add_field(
                        name=f"{subject} Progress",
                        value=f"```\nProgress: {progress:.1f}%\nDays Left: {days_left}\nTopics Completed: {len(completed)}/{len(daily_topics)}```",
                        inline=False
                    )
                except Exception as e:
                    self.logger.error(f"Error processing schedule: {str(e)}")
                    continue

            await ctx.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Error in progress command: {str(e)}")
            await ctx.send("❌ An error occurred while checking your progress.")

    @commands.group(name='tips', invoke_without_command=True)
    async def tips(self, ctx):
        """Study tips management commands"""
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                title="📚 Study Tips Management",
                description="Here's how you can manage your study tips:",
                color=discord.Color.blue()
            )

            commands = [
                ("📝 Create Category", "`!tips category add <name> [description]`\nCreate a new tip category"),
                ("👀 View Categories", "`!tips categories`\nList all your tip categories"),
                ("➕ Add Tip", "`!tips add <category> <tip>`\nAdd a new tip to a category"),
                ("📖 View Tips", "`!tips view <category>`\nView tips in a category"),
                ("❌ Delete Category", "`!tips category delete <name>`\nDelete a category and its tips"),
                ("🗑️ Delete Tip", "`!tips delete <category> <tip_id>`\nDelete a specific tip")
            ]

            for name, value in commands:
                embed.add_field(name=name, value=value, inline=False)

            await ctx.send(embed=embed)

    @tips.command(name='category')
    async def category(self, ctx, action: str, name: str, *, description: str = None):
        """Manage study tip categories"""
        if action.lower() not in ['add', 'delete']:
            await ctx.send("❌ Invalid action. Use 'add' or 'delete'.")
            return

        try:
            cursor = self.db.cursor()
            if action.lower() == 'add':
                cursor.execute('''
                    INSERT INTO study_tip_categories (user_id, category_name, description)
                    VALUES (?, ?, ?)
                ''', (str(ctx.author.id), name, description))
                self.db.commit()
                await ctx.send(f"✅ Created new category: **{name}**")
            else:  # delete
                cursor.execute('''
                    DELETE FROM study_tips WHERE category_id IN 
                    (SELECT id FROM study_tip_categories WHERE user_id = ? AND category_name = ?)
                ''', (str(ctx.author.id), name))
                cursor.execute('''
                    DELETE FROM study_tip_categories WHERE user_id = ? AND category_name = ?
                ''', (str(ctx.author.id), name))
                self.db.commit()
                await ctx.send(f"✅ Deleted category: **{name}** and all its tips")
        except sqlite3.IntegrityError:
            await ctx.send(f"❌ Category **{name}** already exists!")
        except Exception as e:
            self.logger.error(f"Error managing category: {str(e)}")
            await ctx.send("❌ An error occurred while managing the category.")

    @tips.command(name='categories')
    async def list_categories(self, ctx):
        """List all study tip categories"""
        try:
            cursor = self.db.cursor()
            cursor.execute('''
                SELECT category_name, description, 
                       (SELECT COUNT(*) FROM study_tips WHERE category_id = c.id) as tip_count
                FROM study_tip_categories c
                WHERE user_id = ?
                ORDER BY category_name
            ''', (str(ctx.author.id),))

            categories = cursor.fetchall()

            if not categories:
                await ctx.send("📝 You don't have any tip categories yet. Create one with `!tips category add <name>`!")
                return

            embed = discord.Embed(
                title="📚 Your Study Tip Categories",
                description="Here are all your tip categories:",
                color=discord.Color.blue()
            )

            for name, desc, count in categories:
                embed.add_field(
                    name=f"📑 {name} ({count} tips)",
                    value=desc or "No description",
                    inline=False
                )

            embed.set_footer(text="Use !tips view <category> to see tips in a category")
            await ctx.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Error listing categories: {str(e)}")
            await ctx.send("❌ An error occurred while listing categories.")

    @tips.command(name='add')
    async def add_tip(self, ctx, category: str, *, tip: str):
        """Add a new study tip to a category"""
        try:
            cursor = self.db.cursor()
            # Get category ID
            cursor.execute('''
                SELECT id FROM study_tip_categories
                WHERE user_id = ? AND category_name = ?
            ''', (str(ctx.author.id), category))

            result = cursor.fetchone()
            if not result:
                await ctx.send(f"❌ Category **{category}** not found!")
                return

            category_id = result[0]
            cursor.execute('''
                INSERT INTO study_tips (category_id, user_id, tip_content)
                VALUES (?, ?, ?)
            ''', (category_id, str(ctx.author.id), tip))

            self.db.commit()
            await ctx.send(f"✅ Added tip to **{category}**!")

        except Exception as e:
            self.logger.error(f"Error adding tip: {str(e)}")
            await ctx.send("❌ An error occurred while adding the tip.")

    @tips.command(name='view')
    async def view_tips(self, ctx, category: str):
        """View tips in a category"""
        try:
            cursor = self.db.cursor()
            cursor.execute('''
                SELECT t.id, t.tip_content, t.created_at
                FROM study_tips t
                JOIN study_tip_categories c ON t.category_id = c.id
                WHERE t.user_id = ? AND c.category_name = ?
                ORDER BY t.created_at DESC
            ''', (str(ctx.author.id), category))

            tips = cursor.fetchall()
            if not tips:
                await ctx.send(f"📝 No tips found in category **{category}**!")
                return

            embed = discord.Embed(
                title=f"📚 Tips in {category}",
                description="Here are your study tips:",
                color=discord.Color.blue()
            )

            for tip_id, content, created_at in tips:
                date = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')
                embed.add_field(
                    name=f"Tip #{tip_id} (Added: {date})",
                    value=content,
                    inline=False
                )

            embed.set_footer(text=f"Total tips: {len(tips)}")
            await ctx.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Error viewing tips: {str(e)}")
            await ctx.send("❌ An error occurred while viewing tips.")

    @tips.command(name='delete')
    async def delete_tip(self, ctx, category: str, tip_id: int):
        """Delete a specific tip from a category"""
        try:
            cursor = self.db.cursor()
            cursor.execute('''
                DELETE FROM study_tips
                WHERE id = ? AND user_id = ? AND category_id IN 
                    (SELECT id FROM study_tip_categories WHERE category_name = ? AND user_id = ?)
            ''', (tip_id, str(ctx.author.id), category, str(ctx.author.id)))

            if cursor.rowcount > 0:
                self.db.commit()
                await ctx.send(f"✅ Deleted tip #{tip_id} from **{category}**!")
            else:
                await ctx.send(f"❌ Tip #{tip_id} not found in **{category}**!")

        except Exception as e:
            self.logger.error(f"Error deleting tip: {str(e)}")
            await ctx.send("❌ An error occurred while deleting the tip.")

async def setup(bot):
    await bot.add_cog(LearningAssistant(bot))