
import discord
from discord.ext import commands
from typing import Optional
import logging

class Education(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger('discord_bot')

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
            import random
            from question_bank_11 import get_stored_question_11
            subject = subject.lower()
            # Get multiple questions and choose randomly
            questions = []
            for _ in range(3):  # Try to get 3 different questions
                q = get_stored_question_11(subject, topic)
                if q and q not in questions:
                    questions.append(q)
            
            question = random.choice(questions) if questions else None
            
            if not question:
                await ctx.send("❌ Sorry, I couldn't find a question for that subject/topic.")
                return
                
            embed = discord.Embed(
                title="📝 Practice Question",
                description=question['question'],
                color=discord.Color.blue()
            )
            if 'options' in question:
                options_text = "\n".join(question['options'])
                embed.add_field(name="Options:", value=options_text, inline=False)
            await ctx.send(embed=embed)
            
        except Exception as e:
            self.logger.error(f"Error in class_11 command: {e}")
            await ctx.send("❌ An error occurred while getting your question.")

    @commands.command(name='12')
    async def class_12(self, ctx, subject: str, topic: Optional[str] = None):
        """Get a question for class 12"""
        await ctx.send(f"Getting a question for class 12 {subject} {topic if topic else ''}")

    @commands.command(name='subjects')
    async def list_subjects(self, ctx):
        """List all available subjects"""
        subjects = [
            'Mathematics', 'Physics', 'Chemistry', 'Biology',
            'Economics', 'Accountancy', 'Business Studies'
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
