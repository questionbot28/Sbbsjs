import discord
from discord.ext import commands
import google.generativeai as genai
import os
import logging
from typing import Dict, List, Optional
import time
from dotenv import load_dotenv

load_dotenv()

class AIChat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger('discord_bot')
        self.conversations: Dict[int, List[dict]] = {}  # Store user conversations
        self.last_used: Dict[int, float] = {}  # Rate limiting
        self.rate_limit = 5  # Seconds between messages
        self.ai_channel_id = 1340150404775940210  # AI chat channel ID

        # Configure Gemini
        api_key = os.getenv('GOOGLE_AI_API_KEY')
        if not api_key:
            self.logger.error("GOOGLE_AI_API_KEY not found in environment variables")
            raise ValueError("GOOGLE_AI_API_KEY is required")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')

        # Educational context for the AI
        self.system_prompt = """You are EduSphere, an educational AI assistant specialized in helping Class 11 and 12 students.
        You excel at explaining complex topics in simple terms, providing examples, and guiding students through problem-solving.
        Focus on NCERT curriculum topics. Keep responses clear, concise, and educational.
        When appropriate, format mathematical equations and scientific concepts properly.
        If you're unsure about something, admit it and suggest reliable sources for further reading."""

    async def _check_channel(self, ctx) -> bool:
        """Check if command is used in the AI chat channel"""
        if ctx.channel.id != self.ai_channel_id:
            await ctx.send(f"❌ AI chat commands can only be used in <#{self.ai_channel_id}>!")
            return False
        return True

    @commands.command(name="ask")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def ask(self, ctx, *, question: str):
        """Ask any question to the AI assistant"""
        if not await self._check_channel(ctx):
            return

        # Check rate limit
        user_id = ctx.author.id
        current_time = time.time()
        if user_id in self.last_used:
            time_diff = current_time - self.last_used[user_id]
            if time_diff < self.rate_limit:
                await ctx.send(f"⏳ Please wait {int(self.rate_limit - time_diff)} seconds before asking another question!")
                return

        # Send typing indicator
        async with ctx.typing():
            try:
                # Initialize conversation for new users
                if user_id not in self.conversations:
                    self.conversations[user_id] = []
                    chat = self.model.start_chat(history=[])
                    chat.send_message(self.system_prompt)
                else:
                    chat = self.model.start_chat(history=self.conversations[user_id])

                # Get AI response
                response = chat.send_message(question)

                # Update conversation history
                self.conversations[user_id].append({"role": "user", "parts": [question]})
                self.conversations[user_id].append({"role": "model", "parts": [response.text]})

                # Truncate conversation history if too long (keep last 10 messages)
                if len(self.conversations[user_id]) > 20:
                    self.conversations[user_id] = self.conversations[user_id][-20:]

                # Create embed response
                embed = discord.Embed(
                    title="🤖 AI Response",
                    description=response.text[:4096],  # Discord's limit
                    color=discord.Color.blue()
                )
                embed.set_footer(text=f"Asked by {ctx.author.name}")

                # Send response
                await ctx.send(embed=embed)

                # Update rate limit
                self.last_used[user_id] = current_time

            except Exception as e:
                self.logger.error(f"Error in AI response: {str(e)}")
                await ctx.send("❌ Sorry, I encountered an error while processing your question. Please try again later.")

    @commands.command(name="clear_chat")
    async def clear_chat(self, ctx):
        """Clear your chat history with the AI"""
        if not await self._check_channel(ctx):
            return

        user_id = ctx.author.id
        if user_id in self.conversations:
            self.conversations.pop(user_id)
            await ctx.send("✅ Your chat history has been cleared!")
        else:
            await ctx.send("ℹ️ You don't have any chat history to clear!")

    @commands.command(name="aihelp")
    async def ai_help(self, ctx):
        """Show AI chat commands and guidelines"""
        if not await self._check_channel(ctx):
            return

        embed = discord.Embed(
            title="🤖 AI Chat Help",
            description="Get help with your studies using our AI assistant!",
            color=discord.Color.blue()
        )

        commands_info = """
        `!ask <question>` - Ask any question to the AI
        `!clear_chat` - Clear your conversation history
        `!aihelp` - Show this help message
        """
        embed.add_field(name="📝 Commands", value=commands_info, inline=False)

        tips = """
        • Be specific in your questions
        • One question at a time works best
        • For complex topics, break them down
        • Use clear language
        • Wait 5 seconds between questions
        """
        embed.add_field(name="💡 Tips for Best Results", value=tips, inline=False)

        subjects = """
        • Physics
        • Chemistry
        • Mathematics
        • Biology
        • Computer Science
        • English
        And more from NCERT curriculum!
        """
        embed.add_field(name="📚 Supported Subjects", value=subjects, inline=False)

        await ctx.send(embed=embed)

async def setup(bot):
    # Check if API key exists before loading the cog
    if not os.getenv('GOOGLE_AI_API_KEY'):
        raise ValueError("GOOGLE_AI_API_KEY environment variable is required")
    await bot.add_cog(AIChat(bot))