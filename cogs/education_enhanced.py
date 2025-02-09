import discord
from discord.ext import commands
import asyncio
import logging
from typing import Optional, Dict, Any
from question_generator import QuestionGenerator

class Education(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger('discord_bot')
        self.question_generator = QuestionGenerator()
        self.user_questions = {}
        self.command_locks = {}
        self.dm_gif_url = "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExcDI5Y3EydWt1OXgycHh2YnBxbXNyNHV5Y2txdXV6azYyYmx1aHV6dyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/3o7520kCxvPVJAZJZK/giphy.gif"
        self.option_emojis = {
            'A': '🅰️',
            'B': '🅱️',
            'C': '©️',
            'D': '🇩',
        }

    async def send_question_to_dm(self, ctx, question_data: Dict[str, Any]):
        """Send a question to user's DM with fancy formatting"""
        try:
            # Create question embed with emojis
            question_embed = discord.Embed(
                title="📝 Practice Question",
                description=question_data['question'],
                color=discord.Color.blue()
            )

            # Format options with emojis
            if 'options' in question_data:
                options_text = ""
                for i, option in enumerate(question_data['options']):
                    letter = chr(65 + i)  # A, B, C, D
                    emoji = self.option_emojis.get(letter, '⭐')
                    options_text += f"\n{emoji} {option}"

                question_embed.add_field(
                    name="Options:",
                    value=f"```{options_text}```",
                    inline=False
                )

            question_embed.set_footer(text="💫 The answer will be revealed in 60 seconds... 💫")

            # Send question first
            try:
                await ctx.author.send(embed=question_embed)

                # Send confirmation in channel
                channel_embed = discord.Embed(
                    title="📨 Question Generated!",
                    description="I've sent you a DM with the question! Check your private messages.",
                    color=discord.Color.green()
                )
                channel_embed.set_image(url=self.dm_gif_url)
                channel_embed.set_footer(text="Made with ❤️ by Rohanpreet Singh Pathania")
                await ctx.send(embed=channel_embed)

                # Wait 60 seconds
                await asyncio.sleep(60)

                # Create and send answer embed
                if 'correct_answer' in question_data:
                    answer_embed = discord.Embed(
                        title="✨ Answer Revealed! ✨",
                        color=discord.Color.gold()
                    )

                    correct_letter = question_data['correct_answer']
                    emoji = self.option_emojis.get(correct_letter, '✅')

                    answer_text = f"{emoji} The correct answer is {correct_letter}"
                    if 'explanation' in question_data:
                        answer_text += f"\n\n**Explanation:**\n{question_data['explanation']}"

                    answer_embed.description = answer_text
                    await ctx.author.send(embed=answer_embed)

            except discord.Forbidden:
                error_embed = discord.Embed(
                    title="❌ Cannot Send Private Message",
                    description="Please enable direct messages from server members:\n"
                               "Right-click the server icon → Privacy Settings → Enable direct messages",
                    color=discord.Color.red()
                )
                await ctx.send(embed=error_embed)

        except Exception as e:
            self.logger.error(f"Error sending question to DM: {str(e)}")
            await ctx.send("❌ An error occurred while sending the question.")

    @commands.command(name='help')
    async def help_command(self, ctx):
        """Show enhanced help information"""
        help_embed = discord.Embed(
            title="🎓 Educational Bot - Interactive Learning",
            description="Welcome to your personal learning assistant! Here's how to use the bot:",
            color=discord.Color.blue()
        )

        # Main Commands Section
        commands_info = (
            "```ansi\n"
            "[1;34m┏━━━━━ Main Commands ━━━━━┓[0m\n"
            "[1;32m!11[0m - Get Class 11 Questions\n"
            "[1;32m!12[0m - Get Class 12 Questions\n"
            "[1;32m!subjects[0m - List All Subjects\n"
            "[1;34m┗━━━━━━━━━━━━━━━━━━━━━━━┛[0m\n"
            "```"
        )
        help_embed.add_field(
            name="🎮 Available Commands",
            value=commands_info,
            inline=False
        )

        # Usage Examples Section
        examples = (
            "```ansi\n"
            "[1;33m┏━━━━━ Examples ━━━━━┓[0m\n"
            "!11 physics waves\n"
            "!12 chemistry organic\n"
            "!subjects\n"
            "[1;33m┗━━━━━━━━━━━━━━━━━━━┛[0m\n"
            "```"
        )
        help_embed.add_field(
            name="📝 Example Usage",
            value=examples,
            inline=False
        )

        # Features Section
        features = (
            "• 📚 Questions from all major subjects\n"
            "• 🎯 Topic-specific practice\n"
            "• ⏱️ Timed answer reveals\n"
            "• 📨 Private message delivery\n"
            "• 📝 Detailed explanations\n"
            "• 🔄 Regular content updates"
        )
        help_embed.add_field(
            name="✨ Features",
            value=features,
            inline=False
        )

        # Subjects Section
        subjects = (
            "```ansi\n"
            "[1;35m┏━━━━━ Available Subjects ━━━━━┓[0m\n"
            "📕 Mathematics    📗 Physics\n"
            "📘 Chemistry      📙 Biology\n"
            "📔 Economics      📓 Accountancy\n"
            "📒 Business Studies\n"
            "[1;35m┗━━━━━━━━━━━━━━━━━━━━━━━━━━━┛[0m\n"
            "```"
        )
        help_embed.add_field(
            name="📚 Subjects Available",
            value=subjects,
            inline=False
        )

        # Tips Section
        tips = (
            "```ansi\n"
            "[1;36m┏━━━━━ Pro Tips ━━━━━┓[0m\n"
            "• Enable DMs to receive questions\n"
            "• Questions auto-reveal after 60s\n"
            "• Use specific topics for focused practice\n"
            "[1;36m┗━━━━━━━━━━━━━━━━━━━┛[0m\n"
            "```"
        )
        help_embed.add_field(
            name="💡 Tips & Tricks",
            value=tips,
            inline=False
        )

        # Creator Info
        creator_info = (
            "```ansi\n"
            "[0;35m┏━━━━━ Creator Information ━━━━━┓[0m\n"
            "[0;36m┃     Made with 💖 by:          ┃[0m\n"
            "[0;33m┃  Rohanpreet Singh Pathania   ┃[0m\n"
            "[0;36m┃     Language: Python 🐍      ┃[0m\n"
            "[0;35m┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛[0m\n"
            "```"
        )
        help_embed.add_field(
            name="👨‍💻 Credits",
            value=creator_info,
            inline=False
        )

        help_embed.set_footer(text="Use these commands to enhance your learning! 📚✨")
        await ctx.send(embed=help_embed)

    @commands.command(name='11')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def class_11(self, ctx, subject: str, topic: Optional[str] = None):
        """Get a question for class 11"""
        if ctx.channel.id != 1337669136729243658:
            await ctx.send("❌ This command can only be used in the designated channel!")
            return
        await self._handle_question_command(ctx, subject, topic, 11)

    @commands.command(name='12')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def class_12(self, ctx, subject: str, topic: Optional[str] = None):
        """Get a question for class 12"""
        if ctx.channel.id != 1337669207193682001:
            await ctx.send("❌ This command can only be used in the designated channel!")
            return
        await self._handle_question_command(ctx, subject, topic, 12)

    async def _handle_question_command(self, ctx, subject: str, topic: Optional[str], class_level: int):
        """Handle question generation for both class 11 and 12"""
        if ctx.author.id not in self.command_locks:
            self.command_locks[ctx.author.id] = asyncio.Lock()

        async with self.command_locks[ctx.author.id]:
            try:
                # Validate subject
                is_valid, normalized_subject = self._validate_subject(subject)
                if not is_valid:
                    available_subjects = ['Mathematics', 'Physics', 'Chemistry', 'Biology',
                                       'Economics', 'Accountancy', 'Business Studies', 'English']
                    await ctx.send(f"❌ Invalid subject. Available subjects: {', '.join(available_subjects)}")
                    return

                # Initialize tracking for this user and subject
                if ctx.author.id not in self.user_questions:
                    self.user_questions[ctx.author.id] = {}

                # Generate question
                try:
                    question = await self.question_generator.generate_question(
                        subject=normalized_subject,
                        topic=topic,
                        class_level=class_level,
                        user_id=str(ctx.author.id)
                    )

                    if not question:
                        await ctx.send("❌ Unable to generate a question at this time. Please try again.")
                        return

                    # Send question to DM
                    await self.send_question_to_dm(ctx, question)

                except Exception as e:
                    self.logger.error(f"Error generating question: {str(e)}")
                    error_message = str(e)
                    if "API key" in error_message:
                        await ctx.send("❌ There's an issue with the API configuration. Please contact the bot administrator.")
                    else:
                        await ctx.send(f"❌ An error occurred while getting your question: {error_message}")

            except Exception as e:
                self.logger.error(f"Error in question command: {str(e)}")
                await ctx.send("❌ An error occurred while processing your request.")

    def _validate_subject(self, subject: str) -> tuple[bool, str]:
        """Validate and normalize subject name"""
        subject_mapping = {
            'maths': 'mathematics',
            'math': 'mathematics',
            'bio': 'biology',
            'physics': 'physics',
            'chemistry': 'chemistry',
            'economics': 'economics',
            'accountancy': 'accountancy',
            'business': 'business_studies',
            'business_studies': 'business_studies',
            'english': 'english'
        }

        normalized_subject = subject.lower()
        normalized_subject = subject_mapping.get(normalized_subject, normalized_subject)

        if normalized_subject not in subject_mapping.values():
            return False, normalized_subject

        return True, normalized_subject

    @commands.command(name='subjects')
    async def list_subjects(self, ctx):
        """List all available subjects"""
        embed = discord.Embed(
            title="📚 Available Subjects",
            description=(
                "Here are all the subjects you can study!\n"
                "Use them with the !11 or !12 commands:"
            ),
            color=discord.Color.blue()
        )

        subjects_format = (
            "```ansi\n"
            "[1;34m┏━━━━━ Class 11 & 12 Subjects ━━━━━┓[0m\n"
            "📕 Mathematics\n"
            "📗 Physics\n"
            "📘 Chemistry\n"
            "📙 Biology\n"
            "📔 Economics\n"
            "📓 Accountancy\n"
            "📒 Business Studies\n"
            "📚 English\n"
            "[1;34m┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛[0m\n"
            "```"
        )
        
        embed.add_field(
            name="Available Subjects:",
            value=subjects_format,
            inline=False
        )

        embed.add_field(
            name="💡 Quick Tip",
            value="You can also use shortcuts like 'math' for Mathematics and 'bio' for Biology!",
            inline=False
        )

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Education(bot))
