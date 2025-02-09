
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
            question = await self._get_unique_question(ctx, subject, topic, 11)
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
            self.logger.error(f"Error in class_11 command: {e}")
            await ctx.send("❌ An error occurred while getting your question.")

    @commands.command(name='12')
    async def class_12(self, ctx, subject: str, topic: Optional[str] = None):
        """Get a question for class 12"""
        try:
            question = await self._get_unique_question(ctx, subject, topic, 12)
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

    async def _get_unique_question(self, ctx, subject: str, topic: Optional[str], class_level: int):
        """Get a question for the given subject and topic"""
        try:
            from question_generator import QuestionGenerator
            
            # Create question generator instance
            generator = QuestionGenerator()
            
            # Generate new question using OpenAI
            question = await generator.generate_question(
                subject=subject,
                topic=topic,
                class_level=class_level
            )
            
            return question

        except Exception as e:
            self.logger.error(f"Error in _get_unique_question: {e}")
            # Fallback to question bank if OpenAI fails
            import random
            from question_bank_11 import QUESTION_BANK_11
            from question_bank_12 import QUESTION_BANK_12
            
            question_bank = QUESTION_BANK_11 if class_level == 11 else QUESTION_BANK_12
            if subject in question_bank:
                if isinstance(question_bank[subject], dict):
                    questions = question_bank[subject].get(topic.lower(), []) if topic else []
                    if not questions:
                        for topic_questions in question_bank[subject].values():
                            questions.extend(topic_questions)
                else:
                    questions = question_bank[subject]
                    
                if questions:
                    return random.choice(questions)
            return None

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
