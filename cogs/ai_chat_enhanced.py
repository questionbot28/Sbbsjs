
import discord
from discord.ext import commands
import json
import logging
import os
import random
import google.generativeai as genai

class AIChatEnhanced(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger('discord_bot')
        # Initialize Google AI model
        genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
        self.model = genai.GenerativeModel('gemini-pro')

    async def _check_channel(self, ctx):
        """Check if command is used in allowed channel"""
        allowed_channels = ['ai-chat', 'bot-commands']
        return ctx.channel.name in allowed_channels

    @commands.command(name="debate")
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def debate(self, ctx, *, topic: str = None):
        """Generate a debate topic with pros and cons"""
        if not await self._check_channel(ctx):
            return

        loading_msg = await ctx.send("🤔 Generating debate topic...")

        try:
            if topic is None:
                # Generate random topic if none provided
                topics = ["Technology in Education", "Homework", "School Uniforms", 
                         "Distance Learning", "Standardized Testing"]
                topic = random.choice(topics)

            prompt = f"""Generate a balanced debate for the topic: {topic}
            Provide:
            1. Clear title
            2. Supporting arguments (pros)
            3. Opposing arguments (cons)
            Keep each side's arguments concise and clear."""

            response = self.model.generate_content(prompt)
            debate_text = response.text

            # Parse the response into structured data
            debate_data = {
                'title': topic,
                'pros': debate_text.split('Pros:')[1].split('Cons:')[0].strip(),
                'cons': debate_text.split('Cons:')[1].strip()
            }

            embed = discord.Embed(
                title=f"🗣️ Debate Topic: {debate_data['title']}",
                color=discord.Color.blue()
            )

            embed.add_field(
                name="🟢 Supporting Arguments",
                value=f"```{debate_data['pros']}```",
                inline=False
            )

            embed.add_field(
                name="🔴 Opposing Arguments",
                value=f"```{debate_data['cons']}```",
                inline=False
            )

            await loading_msg.delete()
            await ctx.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Error in debate command: {str(e)}")
            await loading_msg.edit(content="❌ An error occurred. Please try again.")

async def setup(bot):
    await bot.add_cog(AIChatEnhanced(bot))
