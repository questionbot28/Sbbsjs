import discord
from discord.ext import commands
import json
import sqlite3
import logging
from datetime import datetime
import asyncio
import openai
import os
from typing import List, Dict, Optional

class Flashcard:
    def __init__(self, front: str, back: str, user_id: str, subject: Optional[str] = None):
        self.front = front
        self.back = back
        self.user_id = user_id
        self.subject = subject
        self.created_at = datetime.now()

class Flashcards(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger('discord_bot')
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
                    user_id TEXT,
                    subject TEXT,
                    front TEXT,
                    back TEXT,
                    created_at TIMESTAMP,
                    last_reviewed TIMESTAMP,
                    review_count INTEGER DEFAULT 0
                )
            ''')
            
            self.db.commit()
            self.logger.info("Flashcards database initialized")
        except Exception as e:
            self.logger.error(f"Error setting up flashcards database: {str(e)}")

    async def generate_flashcards(self, text: str, subject: Optional[str] = None) -> List[Flashcard]:
        """Generate flashcards using OpenAI API"""
        try:
            prompt = (
                f"Convert this text into 3-5 flashcards about {subject if subject else 'the topic'}. "
                "Format: Front: [Question/Term] | Back: [Answer/Definition]\n\n"
                f"Text: {text}"
            )
            
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[{"role": "system", "content": "You are a helpful flashcard creator. Create clear, concise flashcards from the given text."},
                         {"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=500
            )
            
            flashcards_text = response.choices[0].message.content
            flashcard_list = []
            
            # Parse the response into flashcards
            for line in flashcards_text.split('\n'):
                if '|' in line:
                    front, back = line.split('|')
                    front = front.replace('Front:', '').strip()
                    back = back.replace('Back:', '').strip()
                    flashcard_list.append(Flashcard(front, back, None, subject))
            
            return flashcard_list
            
        except Exception as e:
            self.logger.error(f"Error generating flashcards: {str(e)}")
            return []

    @commands.group(name='flashcard', aliases=['fc'])
    async def flashcard(self, ctx):
        """Flashcard command group"""
        if ctx.invoked_subcommand is None:
            await ctx.send("❓ Available commands:\n"
                         "```\n"
                         "!flashcard create <text> [subject] - Create flashcards from text\n"
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
            
            # Generate flashcards
            flashcards = await self.generate_flashcards(content, subject)
            
            if not flashcards:
                await msg.edit(content="❌ Failed to generate flashcards. Please try again.")
                return
            
            # Save flashcards to database
            cursor = self.db.cursor()
            for card in flashcards:
                cursor.execute('''
                    INSERT INTO flashcards (user_id, subject, front, back, created_at)
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (str(ctx.author.id), subject, card.front, card.back))
            
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
            
        except Exception as e:
            self.logger.error(f"Error creating flashcards: {str(e)}")
            await ctx.send("❌ An error occurred while creating flashcards.")

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
