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
                title="Available Subjects",
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
        Example: !question 11 Accountancy "Basic Accounting Terms"
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

            # If topic is provided, get available topics for validation
            if topic:
                available_topics = self.question_generator.get_topics(subject)
                # Try to match the provided topic with available topics (case-insensitive)
                topic = topic.strip()
                matched_topic = next(
                    (t for t in available_topics if t.lower() == topic.lower()),
                    None
                )
                if not matched_topic:
                    topics_list = "\n".join(f"• {t}" for t in available_topics)
                    await ctx.send(f"Invalid topic for {subject}. Available topics are:\n{topics_list}")
                    return
                topic = matched_topic  # Use the correctly cased topic name

            # Initial status message
            status_embed = discord.Embed(
                title="Question Generator",
                description="🔄 Generating question...",
                color=discord.Color.blue()
            )
            status_embed.set_footer(text=f"Requested by {ctx.author.name}")
            status_message = await ctx.send(embed=status_embed)

            # Generate question
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

                # Add correct answer with emoji
                correct_answer = question_data['correct_answer']
                answer_embed.add_field(
                    name="Correct Answer", 
                    value=f"{option_emojis[correct_answer]} Option {correct_answer}", 
                    inline=False
                )

                # Add separator
                answer_embed.add_field(name="\u200b", value="\u200b", inline=False)

                # Add explanation
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
                # Handle locked DMs
                self.logger.warning(f"Could not send DM to user {ctx.author.name} - DMs are locked")
                await ctx.send("❌ Unable to send you a private message. Please check if your DMs are open and try again.")
                return

        except Exception as e:
            self.logger.error(f"Error generating question: {e}")
            await ctx.send("An error occurred while generating the question. Please try again later.")

    @commands.command(name='topics')
    async def list_topics(self, ctx, subject: str, class_level: int = None):
        """Lists all topics for a given subject"""
        try:
            subject = subject.lower()
            if class_level and subject == 'english':
                topics = self.question_generator.get_class_specific_topics(subject, class_level)
                title = f"Topics in {subject.title()} for Class {class_level}"
            else:
                topics = self.question_generator.get_topics(subject)
                title = f"Topics in {subject.title()}"

            if not topics:
                await ctx.send(f"Invalid subject or class level. Use !subjects to see available subjects.")
                return

            embed = discord.Embed(
                title=title,
                description="\n".join(f"• {topic}" for topic in topics),
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
        except Exception as e:
            self.logger.error(f"Error listing topics: {e}")
            await ctx.send("An error occurred while fetching topics. Please try again.")


async def setup(bot):
    await bot.add_cog(Education(bot))