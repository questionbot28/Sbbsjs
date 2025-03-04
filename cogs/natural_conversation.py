import discord
from discord.ext import commands
import logging
import os
import google.generativeai as genai
import asyncio
import random
from collections import deque
from datetime import datetime, timedelta

class NaturalConversation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger('discord_bot')
        self.allowed_channels = {1340150404775940210}  # AI chat channel ID

        # Initialize Gemini AI
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            self.logger.error("Google API key not found in environment variables")
            self.model = None
            return

        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-pro')
            self.logger.info("Successfully initialized Gemini model for natural conversation")
        except Exception as e:
            self.logger.error(f"Failed to initialize Gemini: {str(e)}")
            self.model = None

        # Conversation management
        self.conversation_history = {}  # Channel ID -> list of recent messages
        self.last_response_time = {}  # Channel ID -> datetime
        self.message_queue = {}  # Channel ID -> deque of messages
        self.max_history = 10  # Maximum number of messages to keep per channel
        self.response_cooldown = 5  # Reduced cooldown to 5 seconds for more natural conversation
        self.response_chance = 0.9  # 90% chance to respond when mentioned
        self.ambient_response_chance = 0.4  # 40% chance to respond to general conversation

    def _should_respond(self, message):
        """Determine if the bot should respond to a message"""
        # Don't respond if model isn't initialized
        if not self.model:
            self.logger.warning("Skipping response - Gemini model not initialized")
            return False

        # Don't respond to self or other bots
        if message.author.bot:
            return False

        # Only respond in allowed channels
        if message.channel.id not in self.allowed_channels:
            return False

        # Check cooldown
        now = datetime.now()
        last_response = self.last_response_time.get(message.channel.id)
        if last_response and (now - last_response).total_seconds() < self.response_cooldown:
            return False

        # Higher chance to respond when mentioned or when message is directed at bot
        if self.bot.user in message.mentions or message.content.lower().startswith(('hey bot', 'hi bot', 'hello bot')):
            return random.random() < self.response_chance

        # Random chance to respond to ambient conversation
        return random.random() < self.ambient_response_chance

    def _update_conversation_history(self, message):
        """Update the conversation history for a channel"""
        channel_id = message.channel.id
        if channel_id not in self.conversation_history:
            self.conversation_history[channel_id] = []

        history = self.conversation_history[channel_id]
        history.append({
            'author': str(message.author),
            'content': message.content,
            'timestamp': message.created_at.isoformat()
        })

        # Keep only recent history
        while len(history) > self.max_history:
            history.pop(0)

    async def _generate_response(self, message):
        """Generate a contextual response using conversation history"""
        try:
            if not self.model:
                return None

            channel_id = message.channel.id
            history = self.conversation_history.get(channel_id, [])

            # Build conversation context
            context = (
                "You are a friendly and engaging Discord chat participant. "
                "Keep responses casual, natural, and engaging like a friend in the conversation. "
                "Use informal language and occasional emojis to express emotions. "
                "Keep responses brief (1-2 sentences) unless asked for more detail. "
                "Avoid being overly formal or robotic.\n\n"
            )

            # Add recent message history
            context += "Recent conversation:\n"
            for msg in history[-5:]:  # Use last 5 messages for better context
                context += f"{msg['author']}: {msg['content']}\n"

            # Add the current message and encourage natural response
            context += f"\nRespond naturally to this message: {message.content}\n"
            context += "Remember to keep the response casual and friendly, as if chatting with friends."

            self.logger.debug(f"Generating response with context: {context}")
            response = self.model.generate_content(context)
            response.resolve()

            if not response.text:
                self.logger.warning("Empty response from Gemini")
                return None

            # Clean up the response
            resp_text = response.text.strip()
            # Remove any markdown code blocks or quotes
            resp_text = resp_text.replace('```', '').replace('`', '')
            resp_text = resp_text.replace('> ', '').replace('\n', ' ')

            self.logger.debug(f"Generated response: {resp_text}")
            return resp_text[:2000]  # Discord message length limit

        except Exception as e:
            self.logger.error(f"Error generating response: {str(e)}")
            return None

    @commands.Cog.listener()
    async def on_message(self, message):
        """Listen for messages and respond naturally"""
        try:
            # Skip if we shouldn't respond
            if not self._should_respond(message):
                return

            # Update conversation history
            self._update_conversation_history(message)

            # Generate and send response
            async with message.channel.typing():
                response = await self._generate_response(message)

                if response:
                    # Update cooldown
                    self.last_response_time[message.channel.id] = datetime.now()

                    # Add small random delay to feel more natural
                    delay = random.uniform(1, 2.5)
                    await asyncio.sleep(delay)

                    await message.channel.send(response)
                    self.logger.info(f"Sent natural response in channel {message.channel.id}")

        except Exception as e:
            self.logger.error(f"Error in natural conversation: {str(e)}")

async def setup(bot):
    await bot.add_cog(NaturalConversation(bot))
    logging.getLogger('discord_bot').info("NaturalConversation cog loaded successfully")