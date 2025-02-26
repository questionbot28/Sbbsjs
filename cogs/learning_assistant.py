import discord
from discord.ext import commands
import sqlite3
import logging
import asyncio
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
                model = genai.GenerativeModel('gemini-2.0-flash')
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

            self.db.commit()
            self.logger.info("Learning assistant database initialized")
        except Exception as e:
            self.logger.error(f"Error setting up learning assistant database: {str(e)}")

    @commands.group(name='learn')
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
                model = genai.GenerativeModel('gemini-2.0-flash')
                response = await asyncio.to_thread(model.generate_content, prompt)
                
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

                model = genai.GenerativeModel('gemini-2.0-flash')
                response = await asyncio.to_thread(model.generate_content, prompt)
                
                # Parse the study plan
                import json
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

                model = genai.GenerativeModel('gemini-2.0-flash')
                response = await asyncio.to_thread(model.generate_content, prompt)
                
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

async def setup(bot):
    await bot.add_cog(LearningAssistant(bot))
