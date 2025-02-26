import discord
from discord.ext import commands
import json
import sqlite3
import logging
import asyncio
import google.generativeai as genai
import os
from typing import List, Dict, Optional
from datetime import datetime
from tenacity import retry, stop_after_attempt, wait_exponential

class Flashcard:
    """A class representing a flashcard with front and back content."""
    def __init__(self, front: str, back: str, user_id: str, subject: Optional[str] = None):
        self.front = front
        self.back = back
        self.user_id = user_id
        self.subject = subject
        self.created_at = datetime.now()

class Flashcards(commands.Cog):
    """A cog for managing flashcards with AI-powered generation capabilities."""
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
                # Test model configuration
                model = genai.GenerativeModel('gemini-pro')
                self.logger.info("Successfully initialized Gemini model")
            except Exception as e:
                self.logger.error(f"Failed to configure Gemini: {str(e)}")
        self.setup_database()

    def setup_database(self):
        """Initialize SQLite database for flashcards"""
        try:
            self.db = sqlite3.connect('data/user_data.db')
            cursor = self.db.cursor()

            # Create flashcards table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS flashcards (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    subject TEXT,
                    front TEXT NOT NULL,
                    back TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_reviewed TIMESTAMP,
                    review_count INTEGER DEFAULT 0
                )
            ''')

            self.db.commit()
            self.logger.info("Flashcards database initialized")
        except Exception as e:
            self.logger.error(f"Error setting up flashcards database: {str(e)}")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def _generate_with_gemini(self, prompt: str) -> str:
        """Make API call to Gemini with retry logic"""
        try:
            # List available models for debugging
            self.logger.debug("Available Gemini models:")
            for m in genai.list_models():
                self.logger.debug(f"- {m.name}")

            model = genai.GenerativeModel('gemini-2.0-flash')
            response = await asyncio.to_thread(model.generate_content, prompt)

            # Log response type and structure for debugging
            self.logger.debug(f"Gemini response type: {type(response)}")
            self.logger.debug(f"Gemini response attributes: {dir(response)}")
            self.logger.debug(f"Raw Gemini response: {response.text}")

            if not response.text:
                raise ValueError("Empty response from Gemini")
            return response.text
        except Exception as e:
            if "SERVICE_DISABLED" in str(e):
                self.logger.error("Gemini API service is not enabled. Please enable it in the Google Cloud Console.")
                raise ValueError(
                    "The Gemini AI service needs to be enabled. Please follow these steps:\n"
                    "1. Go to Google Cloud Console\n"
                    "2. Enable the 'Generative Language API'\n"
                    "3. Wait a few minutes for the changes to take effect\n"
                    "Contact the bot administrator for assistance."
                )
            self.logger.error(f"Gemini API call failed: {str(e)}")
            raise

    async def generate_flashcards(self, text: str, user_id: str, subject: Optional[str] = None) -> List[Flashcard]:
        """Generate flashcards using Google's Gemini API"""
        if not os.getenv('GOOGLE_API_KEY'):
            self.logger.error("Google API key not configured")
            raise ValueError("Google API key not configured")

        try:
            # Simplify the prompt to reduce complexity
            prompt = f"""Create 3 flashcards from this text about {subject if subject else 'this topic'}. 
Format each flashcard as:
Front: [Question]
Back: [Answer]

Text: {text}"""

            self.logger.info(f"Generating flashcards for subject: {subject}")
            flashcards_text = await self._generate_with_gemini(prompt)
            self.logger.info("Received response from Gemini")
            self.logger.debug(f"Raw Gemini response: {flashcards_text}")

            flashcard_list = []
            current_front = None

            for line in flashcards_text.split('\n'):
                line = line.strip()
                if not line:
                    continue

                if line.startswith('Front:'):
                    current_front = line.replace('Front:', '').strip()
                elif line.startswith('Back:') and current_front:
                    back = line.replace('Back:', '').strip()
                    if current_front and back:
                        flashcard_list.append(Flashcard(current_front, back, user_id, subject))
                        current_front = None

            if not flashcard_list:
                self.logger.error("No valid flashcards parsed from response")
                self.logger.debug(f"Raw response: {flashcards_text}")
                return []

            self.logger.info(f"Successfully created {len(flashcard_list)} flashcards")
            return flashcard_list

        except ValueError as ve:
            # Handle known errors with specific messages
            self.logger.error(f"Known error in flashcard generation: {str(ve)}")
            raise
        except Exception as e:
            self.logger.error(f"Error in flashcard generation: {str(e)}")
            self.logger.debug(f"Full error details: {str(e)}", exc_info=True)
            return []

    @commands.group(name='flashcard', aliases=['fc'])
    async def flashcard(self, ctx):
        """Flashcard command group"""
        if ctx.invoked_subcommand is None:
            await ctx.send("❓ Available commands:\n"
                         "```\n"
                         "!flashcard create <text> [in subject] - Create flashcards from text\n"
                         "!flashcard review [subject] - Review your flashcards\n"
                         "!flashcard list [subject] - List your flashcards\n"
                         "!flashcard stats - View your flashcard statistics\n"
                         "```")

    @flashcard.command(name='create')
    async def create_flashcards(self, ctx, *, content: str):
        """Create flashcards from text"""
        try:
            # Check if subject is specified
            subject = None
            if ' in ' in content:
                content, subject = content.split(' in ', 1)

            # Send initial response
            msg = await ctx.send("🤖 Generating flashcards... Please wait!")

            try:
                # Generate flashcards
                flashcards = await self.generate_flashcards(content, str(ctx.author.id), subject)

                if not flashcards:
                    await msg.edit(content="❌ Failed to generate flashcards. Please try again.")
                    return

                # Save flashcards to database
                cursor = self.db.cursor()
                for card in flashcards:
                    cursor.execute('''
                        INSERT INTO flashcards (user_id, subject, front, back, created_at)
                        VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                    ''', (card.user_id, card.subject, card.front, card.back))

                self.db.commit()

                # Create embed to show the generated flashcards
                embed = discord.Embed(
                    title="📝 Generated Flashcards",
                    description=f"Created {len(flashcards)} flashcards" + (f" for {subject}" if subject else ""),
                    color=discord.Color.green()
                )

                for i, card in enumerate(flashcards, 1):
                    embed.add_field(
                        name=f"Card {i} - Front",
                        value=card.front,
                        inline=False
                    )
                    embed.add_field(
                        name=f"Card {i} - Back",
                        value=card.back,
                        inline=False
                    )

                await msg.edit(content=None, embed=embed)

            except ValueError as ve:
                error_msg = str(ve)
                if "Gemini AI service needs to be enabled" in error_msg:
                    # Create an embed for the error message
                    error_embed = discord.Embed(
                        title="❌ Configuration Required",
                        description=error_msg,
                        color=discord.Color.red()
                    )
                    await msg.edit(content=None, embed=error_embed)
                else:
                    await msg.edit(content=f"❌ {error_msg}")
            except Exception as e:
                self.logger.error(f"Error creating flashcards: {str(e)}")
                await msg.edit(content="❌ An error occurred while creating flashcards.")

        except Exception as e:
            self.logger.error(f"Error in create_flashcards command: {str(e)}")
            await ctx.send("❌ An error occurred while processing your request.")

    @flashcard.command(name='review')
    async def review_flashcards(self, ctx, subject: Optional[str] = None):
        """Review flashcards interactively"""
        try:
            cursor = self.db.cursor()

            # Get flashcards for review
            if subject:
                cursor.execute('''
                    SELECT id, front, back FROM flashcards 
                    WHERE user_id = ? AND subject = ?
                    ORDER BY last_reviewed ASC NULLS FIRST
                    LIMIT 5
                ''', (str(ctx.author.id), subject))
            else:
                cursor.execute('''
                    SELECT id, front, back FROM flashcards 
                    WHERE user_id = ?
                    ORDER BY last_reviewed ASC NULLS FIRST
                    LIMIT 5
                ''', (str(ctx.author.id),))

            cards = cursor.fetchall()

            if not cards:
                await ctx.send("No flashcards found for review!" + (f" in {subject}" if subject else ""))
                return

            for card_id, front, back in cards:
                embed = discord.Embed(
                    title="🔄 Flashcard Review",
                    description=front,
                    color=discord.Color.blue()
                )
                embed.set_footer(text="React with 👀 to see the answer")

                card_msg = await ctx.send(embed=embed)
                await card_msg.add_reaction("👀")

                def check(reaction, user):
                    return user == ctx.author and str(reaction.emoji) == "👀"

                try:
                    await self.bot.wait_for('reaction_add', timeout=60.0, check=check)

                    # Show answer
                    embed.add_field(name="Answer", value=back, inline=False)
                    await card_msg.edit(embed=embed)

                    # Update review count and timestamp
                    cursor.execute('''
                        UPDATE flashcards 
                        SET review_count = review_count + 1,
                            last_reviewed = CURRENT_TIMESTAMP 
                        WHERE id = ?
                    ''', (card_id,))
                    self.db.commit()

                except asyncio.TimeoutError:
                    await ctx.send("Review session timed out!")
                    break

                # Wait before showing next card
                await asyncio.sleep(2)

        except Exception as e:
            self.logger.error(f"Error reviewing flashcards: {str(e)}")
            await ctx.send("❌ An error occurred during review.")

    @flashcard.command(name='stats')
    async def flashcard_stats(self, ctx):
        """View flashcard statistics"""
        try:
            cursor = self.db.cursor()

            # Get user's flashcard stats
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_cards,
                    COUNT(DISTINCT subject) as subjects,
                    SUM(review_count) as total_reviews,
                    MAX(review_count) as most_reviewed
                FROM flashcards 
                WHERE user_id = ?
            ''', (str(ctx.author.id),))

            stats = cursor.fetchone()

            if not stats or stats[0] == 0:
                await ctx.send("No flashcard statistics available!")
                return

            embed = discord.Embed(
                title="📊 Flashcard Statistics",
                description=f"Statistics for {ctx.author.display_name}",
                color=discord.Color.gold()
            )

            embed.add_field(name="Total Cards", value=stats[0], inline=True)
            embed.add_field(name="Subjects", value=stats[1], inline=True)
            embed.add_field(name="Total Reviews", value=stats[2] or 0, inline=True)
            embed.add_field(name="Most Reviews", value=stats[3] or 0, inline=True)

            await ctx.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Error getting flashcard stats: {str(e)}")
            await ctx.send("❌ An error occurred while fetching statistics.")

async def setup(bot):
    await bot.add_cog(Flashcards(bot))