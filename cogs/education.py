
import discord
from discord.ext import commands
from typing import Optional
import logging
from question_generator import QuestionGenerator

# Store user questions
user_questions = {}

class Education(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.question_generator = QuestionGenerator()
        self.logger = logging.getLogger('discord_bot')

    @commands.command(name='help')
    async def help_command(self, ctx):
        """Show help information"""
        embed = discord.Embed(
            title="📚 Educational Bot Help",
            description="🎓 Greetings, future scholars! I'm your friendly AI study companion, specializing in NCERT curriculum for Classes 11 & 12! \n\n🧠 Whether you're diving into Physics formulas, solving Chemistry equations, or mastering Biology concepts, I'm here to challenge you with carefully crafted questions! \n\nHere's how you can use me:",
            color=discord.Color.blue()
        )

        embed.add_field(
            name="📘 Get Question for Class 11",
            value="```!11 <subject> [topic]```\nExample: !11 physics waves",
            inline=False
        )

        embed.add_field(
            name="📗 Get Question for Class 12",
            value="```!12 <subject> [topic]```\nExample: !12 chemistry electrochemistry",
            inline=False
        )

        embed.add_field(
            name="📋 List Available Subjects",
            value="```!subjects```\nShows all subjects you can study",
            inline=False
        )

        creator_info = (
            "```ansi\n"
            "[0;35m┏━━━━━ Creator Information ━━━━━┓[0m\n"
            "[0;36m┃     Made with 💖 by:          ┃[0m\n"
            "[0;33m┃  Educational Bot Team         ┃[0m\n"
            "[0;36m┃     Language: Python 🐍      ┃[0m\n"
            "[0;35m┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛[0m\n"
            "```"
        )

        embed.add_field(
            name="👨‍💻 Credits",
            value=creator_info,
            inline=False
        )

        embed.set_footer(text="Use these commands to practice and learn! 📚✨")
        await ctx.send(embed=embed)

    @commands.command(name='11')
    async def class_11(self, ctx, subject: str, topic: Optional[str] = None):
        """Get a question for class 11"""
        try:
            subject = subject.lower()
            question = await self.question_generator.generate_question(subject, topic, 11)

            if question:
                question_key = f"{question['question'][:50]}"
                if self._is_question_asked(ctx.author.id, subject, question_key):
                    await ctx.send("🔄 Finding a new question you haven't seen before...")
                    question = await self.question_generator.generate_question(subject, topic, 11)

                if question:
                    self._mark_question_asked(ctx.author.id, subject, question_key)
                    await self._send_question(ctx, question)
                else:
                    await ctx.send("❌ Sorry, couldn't find a new question at this time.")
            else:
                await ctx.send("❌ Sorry, I couldn't find a question for that subject/topic.")
        except Exception as e:
            self.logger.error(f"Error in class_11 command: {e}")
            await ctx.send("❌ An error occurred while getting your question.")

    @commands.command(name='12')
    async def class_12(self, ctx, subject: str, topic: Optional[str] = None):
        """Get a question for class 12"""
        try:
            subject = subject.lower()
            question = await self.question_generator.generate_question(subject, topic, 12)

            if question:
                question_key = f"{question['question'][:50]}"
                if self._is_question_asked(ctx.author.id, subject, question_key):
                    await ctx.send("🔄 Finding a new question you haven't seen before...")
                    question = await self.question_generator.generate_question(subject, topic, 12)

                if question:
                    self._mark_question_asked(ctx.author.id, subject, question_key)
                    await self._send_question(ctx, question)
                else:
                    await ctx.send("❌ Sorry, couldn't find a new question at this time.")
            else:
                await ctx.send("❌ Sorry, I couldn't find a question for that subject/topic.")
        except Exception as e:
            self.logger.error(f"Error in class_12 command: {e}")
            await ctx.send("❌ An error occurred while getting your question.")

    async def _send_question(self, ctx, question: dict):
        """Format and send a question to the channel"""
        embed = discord.Embed(
            title="📝 Practice Question",
            description=question['question'],
            color=discord.Color.blue()
        )

        options_text = "\n".join(question['options'])
        embed.add_field(name="Options:", value=f"```{options_text}```", inline=False)
        await ctx.send(embed=embed)

    def _is_question_asked(self, user_id: int, subject: str, question_key: str) -> bool:
        """Check if a question was already asked to a user"""
        return user_id in user_questions and \
               subject in user_questions.get(user_id, {}) and \
               question_key in user_questions[user_id][subject]

    def _mark_question_asked(self, user_id: int, subject: str, question_key: str):
        """Mark a question as asked for a user"""
        if user_id not in user_questions:
            user_questions[user_id] = {}
        if subject not in user_questions[user_id]:
            user_questions[user_id][subject] = set()
        user_questions[user_id][subject].add(question_key)

async def setup(bot):
    await bot.add_cog(Education(bot))
