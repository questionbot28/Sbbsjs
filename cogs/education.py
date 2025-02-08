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
    async def get_question(self, ctx, subject: str, *, topic: str = None):
        """Generates a question for the specified subject and topic"""
        try:
            subject = subject.lower()
            if subject not in self.question_generator.get_subjects():
                await ctx.send("Invalid subject. Use !subjects to see available subjects.")
                return

            async with ctx.typing():
                question_data = await self.question_generator.generate_question(subject, topic)

            embed = discord.Embed(
                title=f"Question - {subject.title()}" + (f" ({topic})" if topic else ""),
                description=question_data['question'],
                color=discord.Color.blue()
            )

            options_text = "\n".join(question_data['options'])
            embed.add_field(name="Options", value=options_text, inline=False)

            question_message = await ctx.send(embed=embed)

            await asyncio.sleep(30)

            answer_embed = discord.Embed(
                title="Answer",
                description=f"Correct Answer: {question_data['correct_answer']}\n\n"
                           f"Explanation: {question_data['explanation']}",
                color=discord.Color.green()
            )
            await ctx.send(embed=answer_embed)

        except Exception as e:
            self.logger.error(f"Error generating question: {e}")
            await ctx.send("An error occurred while generating the question. Please try again later.")

async def setup(bot):
    await bot.add_cog(Education(bot))