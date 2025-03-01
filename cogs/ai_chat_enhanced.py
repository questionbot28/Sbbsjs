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

    async def _get_ai_response(self, prompt: str, system_message: Optional[str] = None) -> str:
        """Get response from Gemini AI"""
        try:
            combined_prompt = f"{system_message}\n{prompt}" if system_message else prompt
            self.logger.debug(f"Sending request to Gemini AI with prompt: {combined_prompt[:50]}...")

            response = model.generate_content(combined_prompt)
            return response.text
        except Exception as e:
            self.logger.error(f"Error getting AI response: {e}")
            return "❌ An error occurred while processing your request."

    async def _get_image_analysis(self, image_data: bytes, prompt: str) -> str:
        """Analyze image using Gemini Vision AI"""
        try:
            self.logger.debug("Processing image with Gemini Vision API...")
            response = vision_model.generate_content(
                [prompt, {"mime_type": "image/jpeg", "data": image_data}]
            )
            return response.text
        except Exception as e:
            self.logger.error(f"Error analyzing image: {e}")
            return "❌ An error occurred while analyzing the image."

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

                    prompt = (
                        "Analyze this image in detail. Describe what you see, "
                        "identify key elements, and provide relevant insights. "
                        "If there's text in the image, include that in your analysis."
                    )

                    self.logger.debug("Sending image to Gemini Vision API...")
                    response = vision_model.generate_content(
                        [prompt, {"mime_type": "image/jpeg", "data": image_data}]
                    )
                    analysis = response.text

                    embed = discord.Embed(
                        title="🖼️ Image Analysis",
                        description="Here's my analysis of your image:",
                        color=discord.Color.purple()
                    )
                    embed.set_thumbnail(url=attachment.url)

                else:
                    # Handle text analysis
                    self.logger.info(f"Processing text from {ctx.author}")
                    response = model.generate_content(
                        f"Analyze the following text and provide key insights:\n\n{text}"
                    )
                    analysis = response.text

                    embed = discord.Embed(
                        title="📊 Text Analysis",
                        description="Here's my analysis of your text:",
                        color=discord.Color.purple()
                    )
                    embed.add_field(
                        name="Input Text",
                        value=text[:1000] + "..." if len(text) > 1000 else text,
                        inline=False
                    )

                # Add analysis to embed
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
                await ctx.send("❌ An error occurred while processing your request. Please try again later.")

    @commands.command(name='ask')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def ask(self, ctx, *, question: str):
        """Ask AI any question"""
        self.logger.info(f"Ask command received from {ctx.author}: {question[:50]}...")

        if not await self._check_channel(ctx):
            return

        async with ctx.typing():
            answer = await self._get_ai_response(question)

            embed = discord.Embed(
                title="❓ Question & Answer",
                color=discord.Color.blue()
            )

            embed.add_field(
                name="Question",
                value=question,
                inline=False
            )

            embed.add_field(
                name="Answer",
                value=answer,
                inline=False
            )

            await ctx.send(embed=embed)
            self.logger.info(f"Successfully answered question for {ctx.author}")

    @commands.command(name='explain')
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def explain(self, ctx, *, concept: str):
        """Get detailed explanation of a concept"""
        self.logger.info(f"Explain command received from {ctx.author}: {concept[:50]}...")

        if not await self._check_channel(ctx):
            return

        async with ctx.typing():
            system_prompt = (
                "You are a knowledgeable teacher. Explain the following concept clearly "
                "with examples and analogies that would help a student understand better."
            )

            explanation = await self._get_ai_response(concept, system_prompt)

            embed = discord.Embed(
                title=f"📚 Explaining: {concept}",
                description=explanation,
                color=discord.Color.green()
            )

            await ctx.send(embed=embed)
            self.logger.info(f"Successfully explained concept for {ctx.author}")


async def setup(bot):
    cog = AIChatEnhanced(bot)
    await bot.add_cog(cog)
    logging.getLogger('discord_bot').info("AIChatEnhanced cog loaded successfully")