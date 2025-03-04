import discord
from discord.ext import commands
import logging
import os
import asyncio
import random
import json
from datetime import datetime, timedelta
from tenacity import retry, stop_after_attempt, wait_exponential
import http.client

class NaturalConversation(commands.Cog):
    """A cog for AI-powered learning assistance features"""

    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger('discord_bot')

        # Initialize RapidAPI configuration
        self.api_key = "f12a24bbfamsh2ed8a5f6d386a88p121a3djsn480d5e99e5bf"
        self.api_host = "chat-gpt-43.p.rapidapi.com"
        self.logger.info("Successfully initialized RapidAPI configuration")

        # Conversation management
        self.conversation_history = {}
        self.last_response_time = {}
        self.max_history = 10
        self.response_cooldown = 5
        self.response_chance = 1.0
        self.ambient_response_chance = 0.6

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def _generate_content(self, message_text):
        """Generate content using RapidAPI"""
        try:
            self.logger.info(f"Making request to RapidAPI with message: {message_text[:100]}...")

            # Use asyncio.to_thread to run synchronous http.client in async context
            def make_request():
                try:
                    conn = http.client.HTTPSConnection(self.api_host)
                    headers = {
                        'x-rapidapi-key': self.api_key,
                        'x-rapidapi-host': self.api_host
                    }

                    # URL encode the question parameter
                    from urllib.parse import quote
                    encoded_question = quote(message_text)

                    # Log the request details
                    self.logger.debug(f"Request URL: /problem.json?question={encoded_question[:50]}...")

                    conn.request("GET", f"/problem.json?question={encoded_question}", headers=headers)

                    res = conn.getresponse()
                    self.logger.debug(f"Response status: {res.status}")
                    self.logger.debug(f"Response headers: {res.getheaders()}")

                    data = res.read()
                    conn.close()

                    return data.decode("utf-8")
                except Exception as e:
                    self.logger.error(f"HTTP request failed: {e}")
                    raise

            # Execute the HTTP request in a thread pool
            response_text = await asyncio.to_thread(make_request)
            self.logger.debug(f"RapidAPI raw response: {response_text[:200]}...")

            try:
                data = json.loads(response_text)
                self.logger.debug(f"Response data structure: {json.dumps(data, indent=2)}")

                if "text" in data:  # Extract text from response
                    content = data["text"].strip()
                    if content:
                        # Clean up response for Discord
                        content = content.replace('```', '').replace('`', '')  # Remove code blocks
                        content = content.replace('> ', '').replace('\n', ' ')  # Clean formatting
                        content = ' '.join(content.split())  # Normalize whitespace

                        self.logger.info(f"Generated response: {content[:100]}...")
                        return content[:2000]  # Discord message length limit
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