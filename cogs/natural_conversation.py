import discord
from discord.ext import commands
import logging
import os
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
        self.api_url = "https://chatgpt-42.p.rapidapi.com/o3mini"
        self.headers = {
            "content-type": "application/json",
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": "chatgpt-42.p.rapidapi.com"
        }
        self.logger.info("Initialized RapidAPI ChatGPT configuration")

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
        """Generate content with retry logic using RapidAPI ChatGPT"""
        try:
            # Format messages for the o3mini endpoint
            formatted_messages = []
            for msg in messages:
                if msg["role"] == "system":
                    continue  # Skip system messages for this endpoint
                formatted_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })

            payload = {
                "messages": formatted_messages,
                "temperature": 0.7
            }

            self.logger.info(f"Making request to RapidAPI with {len(messages)} messages")
            self.logger.debug(f"Full payload: {json.dumps(payload, indent=2)}")

            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(self.api_url, headers=self.headers, json=payload, timeout=30) as response:
                        response_text = await response.text()
                        self.logger.debug(f"RapidAPI status: {response.status}")
                        self.logger.debug(f"RapidAPI response: {response_text}")
                        self.logger.debug(f"RapidAPI headers: {dict(response.headers)}")

                        if response.status != 200:
                            self.logger.error(f"RapidAPI error (status {response.status}): {response_text}")
                            return None

                        try:
                            data = json.loads(response_text)
                            self.logger.debug(f"Response data structure: {json.dumps(data, indent=2)}")

                            if "text" in data:  # The o3mini endpoint returns response in 'text' field
                                content = data["text"].strip()
                                if content:
                                    self.logger.info(f"Generated response: {content[:100]}...")
                                    return content
                                else:
                                    self.logger.error("Empty text content in response")
                            else:
                                self.logger.error(f"Missing 'text' field in response. Available fields: {list(data.keys())}")
                        except json.JSONDecodeError as e:
                            self.logger.error(f"JSON parse error: {e}, Response: {response_text}")
                        except KeyError as e:
                            self.logger.error(f"Missing key in response: {e}, Data: {data}")
                        except Exception as e:
                            self.logger.error(f"Error processing response: {e}")

            except aiohttp.ClientError as e:
                self.logger.error(f"HTTP request failed: {e}")
            except asyncio.TimeoutError:
                self.logger.error("Request timed out")
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

        # Always respond when mentioned or directly addressed
        if self.bot.user in message.mentions or message.content.lower().startswith(('hey bot', 'hi bot', 'hello bot')):
            self.logger.info(f"Bot mentioned/addressed by {message.author}")
            return True

        # 60% chance to join ongoing conversations
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
        history.append({
            'author': str(message.author),
            'content': message.content,
            'timestamp': message.created_at.isoformat()
        })

        while len(history) > self.max_history:
            history.pop(0)

    async def _generate_response(self, message):
        """Generate a contextual response using conversation history"""
        try:
            channel_id = message.channel.id
            history = self.conversation_history.get(channel_id, [])

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

            # Add recent history
            for msg in history[-5:]:  # Use last 5 messages for context
                messages.append({
                    "role": "user" if msg["author"] != str(self.bot.user) else "assistant",
                    "content": msg["content"]
                })

            # Add current message
            messages.append({
                "role": "user",
                "content": message.content
            })

            response_text = await self._generate_content(messages)
            if not response_text:
                return None

            # Clean up response
            response_text = response_text.strip()
            response_text = response_text.replace('```', '').replace('`', '')
            response_text = response_text.replace('> ', '').replace('\n', ' ')

            return response_text[:2000]  # Discord message length limit

        except Exception as e:
            self.logger.error(f"Error generating response: {e}", exc_info=True)
            return None

    @commands.Cog.listener()
    async def on_message(self, message):
        """Listen for messages and respond naturally"""
        try:
            if not self._should_respond(message):
                return

            self._update_conversation_history(message)

            async with message.channel.typing():
                self.logger.info(f"Generating response for: {message.content}")
                response = await self._generate_response(message)

                if response:
                    self.last_response_time[message.channel.id] = datetime.now()

                    # Add small random delay for natural feel
                    delay = random.uniform(1, 2.5)
                    await asyncio.sleep(delay)

                    await message.channel.send(response)
                    self.logger.info(f"Sent response in channel {message.channel.id}")
                else:
                    self.logger.warning("No response generated")

        except Exception as e:
            self.logger.error(f"Error handling message: {e}", exc_info=True)

async def setup(bot):
    try:
        await bot.add_cog(NaturalConversation(bot))
        logging.getLogger('discord_bot').info("NaturalConversation cog loaded successfully")
    except Exception as e:
        logging.getLogger('discord_bot').error(f"Failed to load NaturalConversation cog: {e}", exc_info=True)
        raise