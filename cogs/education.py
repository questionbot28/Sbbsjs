import discord
from discord.ext import commands
from question_generator import QuestionGenerator
import asyncio
from discord.ext.commands import cooldown, BucketType
import logging

class Education(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.question_generator = QuestionGenerator()
        self.logger = logging.getLogger('discord_bot')

    @commands.command(name='subjects')
    async def list_subjects(self, ctx):
        """Lists all available subjects"""
        try:
            subjects = self.question_generator.get_subjects()
            embed = discord.Embed(
                title="Available Subjects",
                description="\n".join(f"• {subject.title()}" for subject in subjects),
                color=discord.Color.blue()
            )
            await ctx.send(embed=embed)
        except Exception as e:
            self.logger.error(f"Error listing subjects: {e}")
            await ctx.send("An error occurred while fetching subjects. Please try again.")

    @commands.command(name='topics')
    async def list_topics(self, ctx, subject: str):
        """Lists all topics for a given subject"""
        try:
            subject = subject.lower()
            topics = self.question_generator.get_topics(subject)
            if not topics:
                await ctx.send(f"Invalid subject. Use !subjects to see available subjects.")
                return

            embed = discord.Embed(
                title=f"Topics in {subject.title()}",
                description="\n".join(f"• {topic}" for topic in topics),
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
        except Exception as e:
            self.logger.error(f"Error listing topics: {e}")
            await ctx.send("An error occurred while fetching topics. Please try again.")

    @commands.command(name='question')
    @cooldown(1, 30, BucketType.user)
    async def get_question(self, ctx, class_level: int, subject: str, *, topic: str = None):
        """Generates a question for the specified class level, subject and topic"""
        try:
            # Validate class level
            if class_level not in [11, 12]:
                await ctx.send("Please specify either class 11 or 12.")
                return

            subject = subject.lower()
            if subject not in self.question_generator.get_subjects():
                await ctx.send("Invalid subject. Use !subjects to see available subjects.")
                return

            # Send initial "generating" message
            status_embed = discord.Embed(
                title="Question Generator",
                description="🔄 Generating question...",
                color=discord.Color.blue()
            )
            status_embed.set_footer(text=f"Requested by {ctx.author.name}")
            status_message = await ctx.send(embed=status_embed)

            async with ctx.typing():
                question_data = await self.question_generator.generate_question(
                    subject, topic, class_level=class_level
                )

            # Question embed
            embed = discord.Embed(
                title=f"📚 Class {class_level} - {subject.title()}" + (f" ({topic})" if topic else ""),
                description=question_data['question'],
                color=discord.Color.green()
            )
            embed.set_author(name="Question Generator")

            # Add a blank field first to create spacing
            embed.add_field(name="\u200b", value="\u200b", inline=False)

            # Format options with emojis
            option_emojis = {'A': '🅰️', 'B': '🅱️', 'C': '©️', 'D': '🇩'}
            options_text = "\n\n".join(f"{option_emojis[opt[0]]} {opt}" for opt in question_data['options'])
            embed.add_field(name="Options", value=options_text, inline=False)

            embed.set_footer(text=f"Answer will be revealed in 30 seconds • Requested by {ctx.author.name}")

            # Delete the status message and send the question
            await status_message.delete()
            question_message = await ctx.send(embed=embed)

            # Wait 30 seconds before revealing answer
            await asyncio.sleep(30)

            # Answer embed with explanation
            answer_embed = discord.Embed(
                title="✅ Answer Revealed",
                color=discord.Color.brand_green()  # Use Discord's brand green color
            )
            answer_embed.set_author(name="Question Generator")

            # Add the correct answer with emoji
            answer_embed.add_field(
                name="Correct Answer", 
                value=f"{option_emojis[question_data['correct_answer']]} Option {question_data['correct_answer']}", 
                inline=False
            )

            # Add a separator field
            answer_embed.add_field(name="\u200b", value="\u200b", inline=False)

            # Add the explanation
            answer_embed.add_field(
                name="Explanation", 
                value=question_data['explanation'],
                inline=False
            )

            answer_embed.set_footer(text=f"Question completed • Requested by {ctx.author.name}")

            await ctx.send(embed=answer_embed)

        except Exception as e:
            self.logger.error(f"Error generating question: {e}")
            await ctx.send("An error occurred while generating the question. Please try again later.")

async def setup(bot):
    await bot.add_cog(Education(bot))