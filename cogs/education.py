import discord
from discord.ext import commands
from question_generator import QuestionGenerator
import asyncio
from discord.ext.commands import cooldown, BucketType
import logging
from collections import defaultdict

class Education(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.question_generator = QuestionGenerator()
        self.logger = logging.getLogger('discord_bot')
        # Dictionary to track shown questions per user
        # Structure: {user_id: {(subject, topic, class_level): [question_hashes]}}
        self.shown_questions = defaultdict(lambda: defaultdict(set))

    def _get_question_hash(self, question_data):
        """Generate a unique hash for a question based on its content"""
        return hash(f"{question_data['question']}{question_data['correct_answer']}")

    def _has_seen_question(self, user_id, subject, topic, class_level, question_data):
        """Check if user has seen this question before"""
        question_hash = self._get_question_hash(question_data)
        key = (subject, topic, class_level)
        return question_hash in self.shown_questions[user_id][key]

    def _mark_question_as_shown(self, user_id, subject, topic, class_level, question_data):
        """Mark a question as shown to a user"""
        question_hash = self._get_question_hash(question_data)
        key = (subject, topic, class_level)
        self.shown_questions[user_id][key].add(question_hash)

    def get_command_help(self):
        """Returns a dictionary of command categories and their descriptions"""
        return {
            "📚 Class Commands": [
                {
                    "command": "!11 [subject] chapters",
                    "description": "Shows all chapters for Class 11 subjects",
                    "example": "!11 Physics chapters"
                },
                {
                    "command": "!12 [subject] chapters",
                    "description": "Shows all chapters for Class 12 subjects",
                    "example": "!12 Chemistry chapters"
                }
            ],
            "❓ Question Commands": [
                {
                    "command": "!question [class] [subject] [topic]",
                    "description": "Generates a question from specified subject and topic",
                    "example": "!question 11 Physics 'Motion in a Plane'"
                }
            ],
            "📖 Subject List": [
                {
                    "command": "!subjects",
                    "description": "Lists all available subjects",
                    "example": "!subjects"
                }
            ]
        }

    @commands.command(name='help')
    async def help_command(self, ctx):
        """Shows this help message"""
        try:
            # Create the main embed
            help_embed = discord.Embed(
                title="🎓 Educational Bot Help",
                description="Welcome to the Educational Bot! Here are all the commands you can use:",
                color=discord.Color.blue()
            )

            # Add bot information
            help_embed.add_field(
                name="ℹ️ About",
                value="I'm an educational bot designed to help Class 11 and 12 students with NCERT curriculum questions and topics.",
                inline=False
            )

            # Add commands by category
            command_help = self.get_command_help()
            for category, commands in command_help.items():
                # Create a formatted string for all commands in this category
                commands_text = ""
                for cmd in commands:
                    commands_text += f"**{cmd['command']}**\n"
                    commands_text += f"━ {cmd['description']}\n"
                    commands_text += f"━ Example: `{cmd['example']}`\n\n"

                help_embed.add_field(
                    name=category,
                    value=commands_text,
                    inline=False
                )

            # Add footer with additional info
            help_embed.set_footer(
                text="💡 Tip: Use these commands in any channel where the bot is present!"
            )

            await ctx.send(embed=help_embed)

        except Exception as e:
            self.logger.error(f"Error displaying help: {e}")
            await ctx.send("An error occurred while showing the help message. Please try again.")

    @commands.command(name='11')
    async def class_11_chapters(self, ctx, subject: str, action: str = "chapters"):
        """Shows chapters for Class 11 subjects
        Usage: !11 <subject> chapters
        Example: !11 Physics chapters"""
        try:
            if action.lower() != "chapters":
                await ctx.send("Please use the format: `!11 <subject> chapters`")
                return

            subject = subject.lower()
            if subject not in self.question_generator.get_subjects():
                subjects_list = ", ".join(self.question_generator.get_subjects())
                await ctx.send(f"Invalid subject. Available subjects are: {subjects_list}")
                return

            topics = self.question_generator.get_class_specific_topics(subject, 11)

            if not topics:
                await ctx.send(f"No chapters found for {subject} Class 11")
                return

            # Create embed for better formatting
            embed = discord.Embed(
                title=f"📚 Class 11 {subject.title()} Chapters",
                color=discord.Color.blue()
            )

            # Split topics into chunks to avoid hitting Discord's field limit
            chunk_size = 20  # Adjust based on average topic length
            for i in range(0, len(topics), chunk_size):
                chunk = topics[i:i + chunk_size]
                # Create a numbered list of topics
                field_value = "\n".join(f"{j+1}. {topic}" for j, topic in enumerate(chunk, start=i+1))
                embed.add_field(
                    name=f"Chapters {i+1}-{i+len(chunk)}" if i > 0 else "Chapters",
                    value=field_value,
                    inline=False
                )

            await ctx.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Error listing chapters: {e}")
            await ctx.send("An error occurred while fetching chapters. Please try again.")

    @commands.command(name='12')
    async def class_12_chapters(self, ctx, subject: str, action: str = "chapters"):
        """Shows chapters for Class 12 subjects
        Usage: !12 <subject> chapters
        Example: !12 Chemistry chapters"""
        try:
            if action.lower() != "chapters":
                await ctx.send("Please use the format: `!12 <subject> chapters`")
                return

            subject = subject.lower()
            if subject not in self.question_generator.get_subjects():
                subjects_list = ", ".join(self.question_generator.get_subjects())
                await ctx.send(f"Invalid subject. Available subjects are: {subjects_list}")
                return

            topics = self.question_generator.get_class_specific_topics(subject, 12)

            if not topics:
                await ctx.send(f"No chapters found for {subject} Class 12")
                return

            # Create embed for better formatting
            embed = discord.Embed(
                title=f"📚 Class 12 {subject.title()} Chapters",
                color=discord.Color.blue()
            )

            # Split topics into chunks to avoid hitting Discord's field limit
            chunk_size = 20  # Adjust based on average topic length
            for i in range(0, len(topics), chunk_size):
                chunk = topics[i:i + chunk_size]
                # Create a numbered list of topics
                field_value = "\n".join(f"{j+1}. {topic}" for j, topic in enumerate(chunk, start=i+1))
                embed.add_field(
                    name=f"Chapters {i+1}-{i+len(chunk)}" if i > 0 else "Chapters",
                    value=field_value,
                    inline=False
                )

            await ctx.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Error listing chapters: {e}")
            await ctx.send("An error occurred while fetching chapters. Please try again.")

    @commands.command(name='subjects')
    async def list_subjects(self, ctx):
        """Lists all available subjects"""
        try:
            subjects = self.question_generator.get_subjects()
            embed = discord.Embed(
                title="📚 Available Subjects",
                description="\n".join(f"• {subject.title()}" for subject in subjects),
                color=discord.Color.blue()
            )
            await ctx.send(embed=embed)
        except Exception as e:
            self.logger.error(f"Error listing subjects: {e}")
            await ctx.send("An error occurred while fetching subjects. Please try again.")

    @commands.command(name='question')
    @cooldown(1, 30, BucketType.user)
    async def get_question(self, ctx, class_level: int, subject: str, *, topic: str = None):
        """Generates a question for the specified class level, subject and topic
        Usage: !question <class_level> <subject> [topic]
        Example: !question 11 Physics "Motion in a Plane"
        """
        try:
            # Validate class level
            if class_level not in [11, 12]:
                await ctx.send("Please specify either class 11 or 12.")
                return

            # Convert subject to lowercase and validate
            subject = subject.lower()
            if subject not in self.question_generator.get_subjects():
                subjects_list = ", ".join(self.question_generator.get_subjects())
                await ctx.send(f"Invalid subject. Available subjects are: {subjects_list}")
                return

            # Initial status message
            status_embed = discord.Embed(
                title="Question Generator",
                description="🔄 Generating question...",
                color=discord.Color.blue()
            )
            status_embed.set_footer(text=f"Requested by {ctx.author.name}")
            status_message = await ctx.send(embed=status_embed)

            # Generate question
            max_attempts = 5  # Maximum attempts to find a new question
            question_data = None

            async with ctx.typing():
                for _ in range(max_attempts):
                    temp_question = await self.question_generator.generate_question(
                        subject, topic, class_level=class_level
                    )

                    if not self._has_seen_question(ctx.author.id, subject, topic, class_level, temp_question):
                        question_data = temp_question
                        self._mark_question_as_shown(ctx.author.id, subject, topic, class_level, question_data)
                        break

                if not question_data:
                    await ctx.send("You've seen all available questions for this topic! Try a different topic or subject.")
                    return

            # Create and send question embed
            embed = discord.Embed(
                title=f"📚 Class {class_level} - {subject.title()}" + (f" ({topic})" if topic else ""),
                description=question_data['question'],
                color=discord.Color.green()
            )
            embed.set_author(name="Question Generator")

            # Add a blank field for spacing
            embed.add_field(name="\u200b", value="\u200b", inline=False)

            # Format options with emojis
            option_emojis = {'A': '🅰️', 'B': '🅱️', 'C': '©️', 'D': '🇩'}
            options_text = "\n\n".join(f"{option_emojis[opt[0]]} {opt}" for opt in question_data['options'])
            embed.add_field(name="Options", value=options_text, inline=False)

            embed.set_footer(text=f"Answer will be revealed in 30 seconds • Requested by {ctx.author.name}")

            # Delete the status message
            await status_message.delete()

            try:
                # Send question to DM
                await ctx.author.send(embed=embed)
                self.logger.info(f"Successfully sent question to {ctx.author.name}'s DM")

                # Send confirmation in channel
                confirm_embed = discord.Embed(
                    description="Check your private messages for the question. If you do not receive the message, please unlock your private messages.",
                    color=discord.Color.blue()
                )
                await ctx.send(embed=confirm_embed)

                # Wait and send answer
                await asyncio.sleep(30)

                # Answer embed
                answer_embed = discord.Embed(
                    title="✅ Answer Revealed",
                    color=discord.Color.green()
                )
                answer_embed.set_author(name="Question Generator")

                correct_answer = question_data['correct_answer']
                answer_embed.add_field(
                    name="Correct Answer", 
                    value=f"{option_emojis[correct_answer]} Option {correct_answer}", 
                    inline=False
                )

                answer_embed.add_field(name="\u200b", value="\u200b", inline=False)

                answer_embed.add_field(
                    name="Explanation", 
                    value=question_data['explanation'],
                    inline=False
                )

                answer_embed.set_footer(text=f"Question completed • Requested by {ctx.author.name}")

                # Send answer in DM
                await ctx.author.send(embed=answer_embed)
                self.logger.info(f"Successfully sent answer to {ctx.author.name}'s DM")

            except discord.Forbidden:
                self.logger.warning(f"Could not send DM to user {ctx.author.name} - DMs are locked")
                await ctx.send("❌ Unable to send you a private message. Please check if your DMs are open and try again.")
                return

        except Exception as e:
            self.logger.error(f"Error generating question: {e}")
            await ctx.send("An error occurred while generating the question. Please try again later.")

async def setup(bot):
    await bot.add_cog(Education(bot))