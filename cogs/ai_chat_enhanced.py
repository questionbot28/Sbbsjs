import discord
from discord.ext import commands
import logging
import os
import openai
from openai import OpenAI
import json
from typing import Optional

# Initialize OpenAI client
# the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# do not change this unless explicitly requested by the user
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class AIChatEnhanced(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger('discord_bot')
        self.ai_channel_id = 1340150404775940210  # AI commands channel

    async def _check_channel(self, ctx):
        """Check if command is used in the AI channel"""
        if ctx.channel.id != self.ai_channel_id:
            await ctx.send(f"❌ AI commands can only be used in <#{self.ai_channel_id}>!")
            return False
        return True

    async def _get_ai_response(self, prompt: str, system_message: Optional[str] = None) -> str:
        """Get response from OpenAI API"""
        try:
            messages = []
            if system_message:
                messages.append({"role": "system", "content": system_message})
            messages.append({"role": "user", "content": prompt})

            response = client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                temperature=0.7,
                max_tokens=2000
            )
            return response.choices[0].message.content
        except Exception as e:
            self.logger.error(f"Error getting AI response: {e}")
            return "❌ An error occurred while processing your request."

    @commands.command(name='ask')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def ask(self, ctx, *, question: str):
        """Ask AI any question"""
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

    @commands.command(name='explain')
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def explain(self, ctx, *, concept: str):
        """Get detailed explanation of a concept"""
        if not await self._check_channel(ctx):
            return

        async with ctx.typing():
            system_prompt = (
                "You are a knowledgeable teacher. Explain the concept clearly "
                "with examples and analogies when appropriate."
            )

            explanation = await self._get_ai_response(concept, system_prompt)

            embed = discord.Embed(
                title=f"📚 Explaining: {concept}",
                description=explanation,
                color=discord.Color.green()
            )

            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(AIChatEnhanced(bot))