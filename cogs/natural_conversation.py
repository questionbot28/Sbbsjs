import discord
from discord.ext import commands
import logging
import os
import asyncio
import random
import json
from datetime import datetime, timedelta
from tenacity import retry, stop_after_attempt, wait_exponential
import aiohttp
from .personality import BotPersonality

class NaturalConversation(commands.Cog):
    """A cog for AI-powered assistance with personality"""

    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger('discord_bot')
        self.personality = BotPersonality()

        # Initialize OpenRouter configuration
        self.api_key = "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"
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://github.com/replicate/extensions",
            "X-Title": "EduSphere Bot"
        }
        self.logger.info("Initialized OpenRouter configuration")

        # Conversation management - balanced settings
        self.conversation_history = {}
        self.last_response_time = {}
        self.max_history = 5
        self.response_cooldown = 2
        self.response_chance = 0.9  # High chance to respond
        self.ambient_response_chance = 0.4  # Moderate chance for ambient chat

    def _determine_conversation_mode(self, message_content):
        """Determine the appropriate conversation mode based on message content"""
        content_lower = message_content.lower()

        # Log the incoming message for debugging
        self.logger.debug(f"Determining mode for message: {message_content[:50]}...")

        # Check for explicit roast requests
        if any(word in content_lower for word in ['roast', 'insult', 'burn', 'make fun']):
            mode = "roast"
            self.logger.info(f"Detected roast request: {message_content[:50]}")
        # Check for study-related content
        elif any(word in content_lower for word in ['study', 'learn', 'homework', 'explain', 'help me understand']):
            mode = "study"
            self.logger.info(f"Detected study request: {message_content[:50]}")
        # Check for music-related content
        elif any(word in content_lower for word in ['play', 'song', 'music', 'playlist', 'queue']):
            mode = "music"
            self.logger.info(f"Detected music request: {message_content[:50]}")
        # Check for help requests
        elif any(word in content_lower for word in ['help', 'how to', 'what can you do', 'commands']):
            mode = "help"
            self.logger.info(f"Detected help request: {message_content[:50]}")
        # Check for Hindi language
        elif self.personality.detect_language(content_lower) == "hindi":
            mode = "hindi"
            self.logger.info(f"Detected Hindi language: {message_content[:50]}")
        else:
            mode = "default"
            self.logger.info(f"Using default mode for: {message_content[:50]}")

        self.logger.info(f"Selected mode '{mode}' for message")
        return mode

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def _generate_content(self, message_text):
        """Generate content using OpenRouter API"""
        try:
            # Determine mode and get appropriate prompts
            mode = self._determine_conversation_mode(message_text)
            system_prompt = self.personality.get_system_prompt(mode)
            self.logger.info(f"Using mode '{mode}' with system prompt length: {len(system_prompt)}")

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "system", "content": "Guidelines: " + ". ".join(self.personality.get_conversation_rules())},
                {"role": "user", "content": message_text}
            ]

            payload = {
                "model": "google/gemini-2.0-flash-thinking-exp:free",
                "messages": messages,
                "temperature": 0.8  # Slightly higher for more creative responses
            }

            self.logger.info(f"Generating response in {mode} mode...")
            async with aiohttp.ClientSession() as session:
                async with session.post(self.api_url, headers=self.headers, json=payload, timeout=30) as response:
                    response_text = await response.text()
                    self.logger.debug(f"API Response Status: {response.status}")
                    self.logger.debug(f"Raw API Response: {response_text[:200]}...")

                    if response.status != 200:
                        self.logger.error(f"API error: {response_text}")
                        return "Sorry, I'm having a moment! Give me a second to reboot my humor circuits. 🔄"

                    try:
                        data = json.loads(response_text)
                        if "choices" in data and len(data["choices"]) > 0:
                            content = data["choices"][0]["message"]["content"].strip()
                            if content:
                                # Format response with personality
                                content = self.personality.format_message(content, mode)
                                self.logger.info(f"Formatted response with personality (mode: {mode}): {content[:100]}...")

                                # Clean up response
                                content = content.replace('```', '').replace('`', '')  # Remove code blocks
                                content = content.replace('> ', '').replace('\n', ' ')  # Clean formatting
                                content = ' '.join(content.split())  # Normalize whitespace

                                # Ensure appropriate length
                                if len(content) > 2000:
                                    content = content[:1997] + "..."

                                self.logger.info(f"Final response in {mode} mode (length: {len(content)})")
                                return content

                        self.logger.error("Invalid or empty response from API")
                        return "Oops! My witty response generator needs a recharge. Try again! 🔋"

                    except json.JSONDecodeError as e:
                        self.logger.error(f"JSON parse error: {str(e)}")
                        return "Even I get tongue-tied sometimes! Let's try that again. 😅"

        except Exception as e:
            self.logger.error(f"Error generating content: {str(e)}")
            return "Technical difficulties! But don't worry, I'll be back to my chatty self soon! 🛠️"

    def _should_respond(self, message):
        """Determine if the bot should respond to a message"""
        if message.author.bot:
            return False

        # Check cooldown
        now = datetime.now()
        last_response = self.last_response_time.get(message.channel.id)
        if last_response and (now - last_response).total_seconds() < self.response_cooldown:
            return False

        # Always respond to direct mentions or relevant queries
        if (self.bot.user in message.mentions or 
            message.content.lower().startswith(('edusphere', 'edu')) or
            self.personality.should_respect_creator(message.content)):
            return True

        # Random chance to join conversations
        return random.random() < self.ambient_response_chance

    @commands.Cog.listener()
    async def on_message(self, message):
        """Process messages and respond with personality"""
        try:
            if not self._should_respond(message):
                return

            async with message.channel.typing():
                response = await self._generate_content(message.content)
                if response:
                    self.last_response_time[message.channel.id] = datetime.now()
                    await asyncio.sleep(1)  # Brief delay for natural feel
                    await message.channel.send(response)

        except Exception as e:
            self.logger.error(f"Error in message handler: {e}")

async def setup(bot):
    await bot.add_cog(NaturalConversation(bot))
    logging.getLogger('discord_bot').info("NaturalConversation cog loaded with personality configuration")