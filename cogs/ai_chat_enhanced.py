import discord
from discord.ext import commands
import logging
import os
import google.generativeai as genai
from typing import Optional
import base64
from io import BytesIO

# Initialize Gemini AI with newer model
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-2.0-flash')  # Using newer flash model for faster responses
vision_model = genai.GenerativeModel('gemini-2.0-flash')  # Using same model for vision tasks

class AIChatEnhanced(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger('discord_bot')
        self.ai_channel_id = 1340150404775940210  # AI commands channel
        self.logger.info(f"AIChatEnhanced cog initialized with AI channel ID: {self.ai_channel_id}")
        self.last_responses = {}  # Store last AI response for each user

    async def _check_channel(self, ctx):
        """Check if command is used in the AI channel"""
        try:
            if ctx.channel.id != self.ai_channel_id:
                self.logger.warning(f"Command attempted in wrong channel. Expected: {self.ai_channel_id}, Got: {ctx.channel.id}")
                await ctx.send(f"❌ AI commands can only be used in <#{self.ai_channel_id}>!")
                return False
            self.logger.debug(f"Channel check passed for command in channel {ctx.channel.id}")
            return True
        except Exception as e:
            self.logger.error(f"Error in channel check: {e}")
            return False

    @commands.command(name='analyze')
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def analyze(self, ctx, *, text: Optional[str] = None):
        """Analyze text or image and provide insights"""
        self.logger.info(f"Analyze command received from {ctx.author}")

        if not await self._check_channel(ctx):
            return

        if not ctx.message.attachments and not text:
            await ctx.send("❌ Please provide either text to analyze or attach an image!")
            return

        async with ctx.typing():
            try:
                if ctx.message.attachments:
                    # Handle image analysis
                    attachment = ctx.message.attachments[0]
                    if not attachment.content_type.startswith('image/'):
                        await ctx.send("❌ Please provide a valid image file!")
                        return

                    self.logger.info(f"Processing image from {ctx.author}")
                    image_data = await attachment.read()

                    # Convert image data to base64
                    image_parts = [
                        {
                            "mime_type": attachment.content_type,
                            "data": base64.b64encode(image_data).decode('utf-8')
                        }
                    ]

                    prompt = (
                        "You are an expert image analyzer. Analyze this image in detail. "
                        "Describe what you see, identify key elements, and provide relevant insights. "
                        "If there's text in the image, include that in your analysis."
                    )

                    self.logger.debug("Sending image to Gemini Vision API...")
                    try:
                        response = vision_model.generate_content([prompt, image_parts[0]])
                        response.resolve()
                        analysis = response.text
                    except Exception as e:
                        self.logger.error(f"Gemini Vision API error: {e}")
                        raise Exception("Failed to analyze image with Gemini Vision API")

                    embed = discord.Embed(
                        title="🖼️ Image Analysis",
                        description="Here's my analysis of your image:",
                        color=discord.Color.purple()
                    )
                    embed.set_thumbnail(url=attachment.url)

                else:
                    # Handle text analysis
                    self.logger.info(f"Processing text from {ctx.author}")
                    try:
                        response = model.generate_content(
                            f"Analyze the following text and provide key insights:\n\n{text}"
                        )
                        response.resolve()
                        analysis = response.text
                    except Exception as e:
                        self.logger.error(f"Gemini text analysis error: {e}")
                        raise Exception("Failed to analyze text with Gemini API")

                    embed = discord.Embed(
                        title="📊 Text Analysis",
                        description="Here's my analysis of your text:",
                        color=discord.Color.purple()
                    )
                    if text:
                        embed.add_field(
                            name="Input Text",
                            value=text[:1000] + "..." if len(text) > 1000 else text,
                            inline=False
                        )

                # Store the analysis as the last response for this user
                self.last_responses[ctx.author.id] = analysis

                # Get the voice commands cog to update its last response
                voice_cog = self.bot.get_cog('VoiceCommands')
                if voice_cog:
                    voice_cog.last_responses[ctx.author.id] = analysis

                # Split analysis into chunks if it's too long
                if len(analysis) > 1024:
                    chunks = [analysis[i:i + 1024] for i in range(0, len(analysis), 1024)]
                    for i, chunk in enumerate(chunks):
                        embed.add_field(
                            name=f"Analysis {i+1}/{len(chunks)}" if len(chunks) > 1 else "Analysis",
                            value=chunk,
                            inline=False
                        )
                else:
                    embed.add_field(
                        name="Analysis",
                        value=analysis,
                        inline=False
                    )

                await ctx.send(embed=embed)
                self.logger.info(
                    f"Successfully analyzed {'image' if ctx.message.attachments else 'text'} "
                    f"for {ctx.author}"
                )

            except Exception as e:
                self.logger.error(f"Error processing {'image' if ctx.message.attachments else 'text'}: {e}")
                error_message = (
                    "❌ An error occurred while processing your request. "
                    "This might be due to the image format or size. "
                    "Please try again with a different image or format."
                ) if ctx.message.attachments else (
                    "❌ An error occurred while processing your text. Please try again."
                )
                await ctx.send(error_message)

    @commands.command(name='ask')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def ask(self, ctx, *, question: str):
        """Ask AI any question"""
        if not await self._check_channel(ctx):
            return

        async with ctx.typing():
            try:
                response = model.generate_content(question)
                response.resolve()
                answer = response.text

                # Store the answer as the last response for this user
                self.last_responses[ctx.author.id] = answer

                # Get the voice commands cog to update its last response
                voice_cog = self.bot.get_cog('VoiceCommands')
                if voice_cog:
                    voice_cog.last_responses[ctx.author.id] = answer

                embed = discord.Embed(
                    title="❓ Question & Answer",
                    color=discord.Color.blue()
                )

                embed.add_field(
                    name="Question",
                    value=question,
                    inline=False
                )

                # Split answer into chunks if it's too long
                if len(answer) > 1024:
                    chunks = [answer[i:i + 1024] for i in range(0, len(answer), 1024)]
                    for i, chunk in enumerate(chunks):
                        embed.add_field(
                            name=f"Answer {i+1}/{len(chunks)}" if len(chunks) > 1 else "Answer",
                            value=chunk,
                            inline=False
                        )
                else:
                    embed.add_field(
                        name="Answer",
                        value=answer,
                        inline=False
                    )

                await ctx.send(embed=embed)
                self.logger.info(f"Successfully answered question for {ctx.author}")
            except Exception as e:
                self.logger.error(f"Error processing question: {e}")
                await ctx.send("❌ An error occurred while processing your question. Please try again.")

    @commands.command(name='explain')
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def explain(self, ctx, *, concept: str):
        """Get detailed explanation of a concept"""
        if not await self._check_channel(ctx):
            return

        async with ctx.typing():
            try:
                prompt = (
                    "You are a knowledgeable teacher. Explain the following concept clearly "
                    "with examples and analogies that would help a student understand better:\n\n"
                    f"{concept}"
                )

                response = model.generate_content(prompt)
                response.resolve()
                explanation = response.text

                # Store the explanation as the last response for this user
                self.last_responses[ctx.author.id] = explanation

                # Get the voice commands cog to update its last response
                voice_cog = self.bot.get_cog('VoiceCommands')
                if voice_cog:
                    voice_cog.last_responses[ctx.author.id] = explanation

                embed = discord.Embed(
                    title=f"📚 Explaining: {concept}",
                    color=discord.Color.green()
                )

                # Split explanation into chunks if it's too long
                if len(explanation) > 1024:
                    chunks = [explanation[i:i + 1024] for i in range(0, len(explanation), 1024)]
                    for i, chunk in enumerate(chunks):
                        embed.add_field(
                            name=f"Explanation {i+1}/{len(chunks)}" if len(chunks) > 1 else "Explanation",
                            value=chunk,
                            inline=False
                        )
                else:
                    embed.add_field(
                        name="Explanation",
                        value=explanation,
                        inline=False
                    )

                await ctx.send(embed=embed)
                self.logger.info(f"Successfully explained concept for {ctx.author}")
            except Exception as e:
                self.logger.error(f"Error explaining concept: {e}")
                await ctx.send("❌ An error occurred while explaining the concept. Please try again.")

async def setup(bot):
    cog = AIChatEnhanced(bot)
    await bot.add_cog(cog)
    logging.getLogger('discord_bot').info("AIChatEnhanced cog loaded successfully")