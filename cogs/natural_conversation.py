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
    """A cog for AI-powered learning assistance features"""

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
            "HTTP-Referer": "https://github.com/replicate/extensions", # Required by OpenRouter
            "X-Title": "EduSphere Bot"  # Name of your application
        }
        self.logger.info("Successfully initialized OpenRouter configuration")

        # Conversation management
        self.conversation_history = {}
        self.last_response_time = {}
        self.max_history = 10
        self.response_cooldown = 5
        self.response_chance = 1.0
        self.ambient_response_chance = 0.6

    def _determine_conversation_mode(self, message_content):
        """Determine the appropriate conversation mode based on message content"""
        content_lower = message_content.lower()

        mode = "default"
        if any(word in content_lower for word in ['study', 'learn', 'homework', 'exam']):
            mode = "study"
        elif any(word in content_lower for word in ['play', 'song', 'music', 'playlist']):
            mode = "music"
        elif any(word in content_lower for word in ['roast', 'insult', 'burn']):
            mode = "roast"

        self.logger.info(f"Determined conversation mode: {mode} for message: {message_content[:50]}...")
        return mode

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def _generate_content(self, message_text):
        """Generate content using OpenRouter API"""
        try:
            # Determine conversation mode
            mode = self._determine_conversation_mode(message_text)

            # Get appropriate system prompt
            system_prompt = self.personality.get_system_prompt(mode)
            self.logger.info(f"Using personality mode: {mode} with system prompt length: {len(system_prompt)}")

            # Format the conversation with system message and personality
            messages = [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "system",
                    "content": "Rules: " + "\n".join(self.personality.get_conversation_rules())
                },
                {
                    "role": "user",
                    "content": message_text
                }
            ]

            payload = {
                "model": "google/gemini-2.0-flash-thinking-exp:free",
                "messages": messages,
                "temperature": 0.7
            }

            self.logger.info(f"Making request to OpenRouter with mode {mode} and message: {message_text[:100]}...")
            self.logger.debug(f"Full payload: {json.dumps(payload, indent=2)}")

            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(self.api_url, headers=self.headers, json=payload, timeout=30) as response:
                        response_text = await response.text()
                        self.logger.debug(f"OpenRouter status: {response.status}")
                        self.logger.debug(f"OpenRouter response: {response_text}")

                        if response.status != 200:
                            self.logger.error(f"OpenRouter error (status {response.status}): {response_text}")
                            return None

                        try:
                            data = json.loads(response_text)
                            self.logger.debug(f"Response data structure: {json.dumps(data, indent=2)}")

                            if "choices" in data and len(data["choices"]) > 0:
                                content = data["choices"][0]["message"]["content"].strip()
                                if content:
                                    # Format response according to personality
                                    content = self.personality.format_message(content, mode)
                                    self.logger.info(f"Formatted response with personality (mode: {mode}): {content[:100]}...")

                                    # Clean up response for Discord
                                    content = content.replace('```', '').replace('`', '')  # Remove code blocks
                                    content = content.replace('> ', '').replace('\n', ' ')  # Clean formatting
                                    content = ' '.join(content.split())  # Normalize whitespace

                                    self.logger.info(f"Final cleaned response: {content[:100]}...")
                                    return content[:2000]  # Discord message length limit
                                else:
                                    self.logger.error("Empty content in API response")
                            else:
                                self.logger.error(f"Invalid response format. Available fields: {list(data.keys())}")
                        except json.JSONDecodeError as e:
                            self.logger.error(f"JSON parse error: {e}, Response: {response_text}")
                        except KeyError as e:
                            self.logger.error(f"Missing key in response: {e}, Data: {data}")
                        except Exception as e:
                            self.logger.error(f"Error processing response: {e}")

            except aiohttp.ClientError as e:
                self.logger.error(f"HTTP request failed: {e}")
            except asyncio.TimeoutError:
                self.logger.error("Request timed out (30s limit)")
            except Exception as e:
                self.logger.error(f"Request error: {e}")

            return None

        except Exception as e:
            self.logger.error(f"Error in _generate_content: {e}", exc_info=True)
            return None

    def _should_respond(self, message):
        """Determine if the bot should respond to a message"""
        if message.author.bot:
            return False

        # Check cooldown
        now = datetime.now()
        last_response = self.last_response_time.get(message.channel.id)
        if last_response and (now - last_response).total_seconds() < self.response_cooldown:
            return False

        # Always respond when mentioned, addressed, or creator is mentioned
        if (self.bot.user in message.mentions or 
            message.content.lower().startswith(('hey bot', 'hi bot', 'hello bot')) or
            self.personality.should_respect_creator(message.content)):
            self.logger.info(f"Bot mentioned/addressed by {message.author}")
            return True

        # Random chance to join conversations
        should_join = random.random() < self.ambient_response_chance
        if should_join:
            self.logger.info(f"Joining conversation with {message.author}")
        return should_join

    def _update_conversation_history(self, message):
        """Update the conversation history for a channel"""
        channel_id = message.channel.id
        if channel_id not in self.conversation_history:
            self.conversation_history[channel_id] = []

        history = self.conversation_history[channel_id]
        history.append(message.content)

        while len(history) > self.max_history:
            history.pop(0)

    @commands.Cog.listener()
    async def on_message(self, message):
        """Listen for messages and respond naturally"""
        try:
            if not self._should_respond(message):
                return

            self._update_conversation_history(message)

            async with message.channel.typing():
                self.logger.info(f"Generating response for: {message.content}")
                response = await self._generate_content(message.content)

                if response:
                    self.last_response_time[message.channel.id] = datetime.now()

                    # Add small random delay for natural feel
                    delay = random.uniform(1, 2.5)
                    await asyncio.sleep(delay)

                    # Pre-send logging
                    self.logger.info(f"About to send response to channel {message.channel.id}: {response[:100]}...")

                    await message.channel.send(response)
                    self.logger.info(f"Successfully sent response in channel {message.channel.id}")
                else:
                    self.logger.warning("No response generated")

        except Exception as e:
            self.logger.error(f"Error in message handler: {e}", exc_info=True)

async def setup(bot):
    try:
        await bot.add_cog(NaturalConversation(bot))
        logging.getLogger('discord_bot').info("NaturalConversation cog loaded successfully")
    except Exception as e:
        logging.getLogger('discord_bot').error(f"Failed to load NaturalConversation cog: {e}", exc_info=True)
        raise