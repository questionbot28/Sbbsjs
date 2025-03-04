import discord
from discord.ext import commands
import logging
import os
import requests
import asyncio
import random
from collections import deque
from datetime import datetime, timedelta
from tenacity import retry, stop_after_attempt, wait_exponential
import json
import aiohttp

class NaturalConversation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger('discord_bot')

        # Initialize RapidAPI configuration
        self.api_key = "f12a24bbfamsh2ed8a5f6d386a88p121a3djsn480d5e99e5bf"
        self.api_url = "https://openai80.p.rapidapi.com/chat/completions"
        self.headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": "openai80.p.rapidapi.com",
            "Content-Type": "application/json"
        }
        self.logger.info("Initialized RapidAPI GPT-4 configuration")

        # Conversation management
        self.conversation_history = {}  # Channel ID -> list of recent messages
        self.last_response_time = {}  # Channel ID -> datetime
        self.message_queue = {}  # Channel ID -> deque of messages
        self.max_history = 10  # Maximum number of messages to keep per channel
        self.response_cooldown = 5  # 5 seconds between responses
        self.response_chance = 1.0  # 100% chance to respond when mentioned
        self.ambient_response_chance = 0.6  # 60% chance to join ongoing conversations

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def _generate_content(self, messages):
        """Generate content with retry logic using GPT-4 API"""
        try:
            self.logger.info("Attempting to generate content with GPT-4")

            payload = {
                "model": "gpt-4",
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 150,
                "top_p": 0.9,
                "frequency_penalty": 0,
                "presence_penalty": 0
            }

            self.logger.debug(f"GPT-4 API payload: {json.dumps(payload, indent=2)}")

            async with aiohttp.ClientSession() as session:
                async with session.post(self.api_url, headers=self.headers, json=payload) as response:
                    response_text = await response.text()
                    self.logger.debug(f"GPT-4 API raw response: {response_text}")

                    try:
                        data = json.loads(response_text)
                        if "choices" in data and data["choices"]:
                            content = data["choices"][0]["message"]["content"]
                            self.logger.info(f"Successfully generated content: {content[:100]}...")
                            return content
                        else:
                            self.logger.error(f"Invalid response format: {response_text}")
                    except json.JSONDecodeError as e:
                        self.logger.error(f"Failed to parse JSON response: {str(e)}")
                    except KeyError as e:
                        self.logger.error(f"Missing key in response: {str(e)}")

                    return None

        except Exception as e:
            self.logger.error(f"Error generating content: {str(e)}")
            raise

    def _should_respond(self, message):
        """Determine if the bot should respond to a message"""
        # Don't respond to self or other bots
        if message.author.bot:
            return False

        # Check cooldown
        now = datetime.now()
        last_response = self.last_response_time.get(message.channel.id)
        if last_response and (now - last_response).total_seconds() < self.response_cooldown:
            return False

        # Always respond when mentioned or directly addressed
        if self.bot.user in message.mentions or message.content.lower().startswith(('hey bot', 'hi bot', 'hello bot')):
            self.logger.info(f"Bot mentioned/addressed by {message.author} - responding with 100% chance")
            return True

        # 60% chance to join ongoing conversations
        should_join = random.random() < self.ambient_response_chance
        if should_join:
            self.logger.info(f"Joining conversation with {message.author} (60% chance triggered)")
        return should_join

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
            channel_id = message.channel.id
            history = self.conversation_history.get(channel_id, [])

            # Format conversation for GPT-4
            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are a friendly and engaging Discord chat participant. "
                        "Keep responses casual and natural, like a friend in the conversation. "
                        "Use informal language and occasional emojis to express emotions. "
                        "Keep responses brief (1-2 sentences) unless asked for more detail. "
                        "Avoid being overly formal or robotic."
                    )
                }
            ]

            # Add recent message history
            for msg in history[-5:]:  # Use last 5 messages for context
                messages.append({
                    "role": "user" if msg["author"] != str(self.bot.user) else "assistant",
                    "content": msg["content"]
                })

            # Add the current message
            messages.append({
                "role": "user",
                "content": message.content
            })

            self.logger.info(f"Attempting to generate response for message: {message.content}")
            response_text = await self._generate_content(messages)

            if not response_text:
                self.logger.warning("Empty response from GPT-4")
                return None

            # Clean up the response
            response_text = response_text.strip()
            response_text = response_text.replace('```', '').replace('`', '')
            response_text = response_text.replace('> ', '').replace('\n', ' ')

            self.logger.info(f"Generated response: {response_text[:100]}...")
            return response_text[:2000]  # Discord message length limit

        except Exception as e:
            self.logger.error(f"Error in _generate_response: {str(e)}")
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
                self.logger.info(f"Generating response to message: {message.content}")
                response = await self._generate_response(message)

                if response:
                    # Update cooldown
                    self.last_response_time[message.channel.id] = datetime.now()

                    # Add small random delay to feel more natural
                    delay = random.uniform(1, 2.5)
                    await asyncio.sleep(delay)

                    await message.channel.send(response)
                    self.logger.info(f"Sent natural response in channel {message.channel.id}")
                else:
                    self.logger.warning("No response generated")

        except Exception as e:
            self.logger.error(f"Error in natural conversation: {str(e)}")

async def setup(bot):
    await bot.add_cog(NaturalConversation(bot))
    logging.getLogger('discord_bot').info("NaturalConversation cog loaded successfully")