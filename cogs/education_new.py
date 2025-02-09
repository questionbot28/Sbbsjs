
import discord
from discord.ext import commands
from typing import Optional
import logging
from question_generator import QuestionGenerator

class Education(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger('discord_bot')
        self.question_generator = QuestionGenerator()

    @commands.command(name='help')
    async def help_command(self, ctx):
        """Show help information"""
        embed = discord.Embed(
            title="📚 Educational Bot Help",
            description="Here are the available commands:",
            color=discord.Color.blue()
        )

        embed.add_field(
            name="📘 Get Question for Class 11",
            value="```!11 <subject> [topic]```\nExample: !11 physics waves",
            inline=False
        )

        embed.add_field(
            name="📗 Get Question for Class 12", 
            value="```!12 <subject> [topic]```\nExample: !12 chemistry organic",
            inline=False
        )

        embed.add_field(
            name="📋 List Available Subjects",
            value="```!subjects```\nShows all subjects you can study",
            inline=False
        )

        embed.set_footer(text="Use these commands to practice and learn! 📚✨")
        await ctx.send(embed=embed)

    @commands.command(name='11')
    async def class_11(self, ctx, subject: str, topic: Optional[str] = None):
        """Get a question for class 11"""
        try:
            subject_mapping = {
                'maths': 'mathematics',
                'math': 'mathematics',
                'bio': 'biology',
                'physics': 'physics',
                'chemistry': 'chemistry',
                'economics': 'economics',
                'accountancy': 'accountancy',
                'business': 'business_studies',
                'business_studies': 'business_studies'
            }

            subject = subject.lower()
            subject = subject_mapping.get(subject, subject)

            question = await self.question_generator.generate_question(subject, topic, 11)
            if question:
                embed = discord.Embed(
                    title="📝 Practice Question",
                    description=question['question'],
                    color=discord.Color.blue()
                )
                if 'options' in question:
                    options_text = "\n".join(question['options'])
                    embed.add_field(name="Options:", value=options_text, inline=False)
                await ctx.send(embed=embed)
            else:
                available_subjects = list(subject_mapping.keys())
                await ctx.send(f"❌ Sorry, I couldn't find a question for that subject/topic.\nAvailable subjects: {', '.join(available_subjects)}")

        except Exception as e:
            self.logger.error(f"Error in class_11 command: {e}")
            await ctx.send("❌ An error occurred while getting your question.")

    @commands.command(name='12')
    async def class_12(self, ctx, subject: str, topic: Optional[str] = None):
        """Get a question for class 12"""
        try:
            question = await self.question_generator.generate_question(subject, topic, 12)
            if question:
                embed = discord.Embed(
                    title="📝 Practice Question",
                    description=question['question'],
                    color=discord.Color.blue()
                )
                if 'options' in question:
                    options_text = "\n".join(question['options'])
                    embed.add_field(name="Options:", value=options_text, inline=False)
                await ctx.send(embed=embed)
            else:
                await ctx.send("❌ Sorry, I couldn't find a question for that subject/topic.")
        except Exception as e:
            self.logger.error(f"Error in class_12 command: {e}")
            await ctx.send("❌ An error occurred while getting your question.")

    @commands.command(name='subjects')
    async def list_subjects(self, ctx):
        """List all available subjects"""
        subjects = [
            'Mathematics',
            'Physics',
            'Chemistry',
            'Biology',
            'Economics',
            'Accountancy',
            'Business Studies'
        ]

        embed = discord.Embed(
            title="📚 Available Subjects",
            description="Here are all the subjects you can study:",
            color=discord.Color.blue()
        )

        subject_list = "\n".join([f"• {subject}" for subject in subjects])
        embed.add_field(name="Subjects:", value=f"```{subject_list}```", inline=False)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Education(bot))
