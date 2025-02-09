import os
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
import logging
from utils.logger import setup_logger
from difflib import get_close_matches
import asyncio

# Load environment variables
load_dotenv()

# Setup logging
logger = setup_logger()

# Bot configuration
COMMAND_PREFIX = '!'
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

class EducationalBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=COMMAND_PREFIX, intents=intents, help_command=None)
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5
        self.reconnect_delay = 5
        self.last_heartbeat = None
        self.heartbeat_timeout = 120  # 2 minutes

    async def setup_hook(self):
        # Start background tasks
        self.check_connection.start()
        self.monitor_heartbeat.start()
        await self.load_extensions()

    async def load_extensions(self):
        try:
            await self.load_extension('cogs.education')
            await self.load_extension('cogs.admin')
            logger.info("Successfully loaded all extensions")
        except Exception as e:
            logger.error(f"Failed to load extensions: {e}")

    @tasks.loop(seconds=30)
    async def check_connection(self):
        """Check bot's connection status periodically"""
        if not self.is_closed():
            logger.debug("Bot connection check: Connected")
            self.last_heartbeat = asyncio.get_event_loop().time()
        else:
            logger.warning("Bot connection check: Disconnected")
            await self.handle_reconnection()

    @tasks.loop(seconds=30)
    async def monitor_heartbeat(self):
        """Monitor the bot's heartbeat and reconnect if necessary"""
        if self.last_heartbeat:
            current_time = asyncio.get_event_loop().time()
            time_since_last_heartbeat = current_time - self.last_heartbeat

            if time_since_last_heartbeat > self.heartbeat_timeout:
                logger.warning(f"Heartbeat timeout detected. Last heartbeat was {time_since_last_heartbeat:.2f} seconds ago")
                await self.handle_reconnection()

    async def handle_reconnection(self):
        """Handle reconnection attempts"""
        if self.reconnect_attempts < self.max_reconnect_attempts:
            self.reconnect_attempts += 1
            logger.info(f"Attempting to reconnect... (Attempt {self.reconnect_attempts}/{self.max_reconnect_attempts})")
            try:
                await self.close()
                await asyncio.sleep(self.reconnect_delay)
                await self.start(os.getenv('DISCORD_TOKEN'))
            except Exception as e:
                logger.error(f"Reconnection attempt failed: {e}")
        else:
            logger.critical("Maximum reconnection attempts reached. Please check the bot's token and internet connection.")
            # Reset attempts after a longer delay
            await asyncio.sleep(300)  # 5 minutes
            self.reconnect_attempts = 0

    async def on_ready(self):
        """Called when the bot is ready and connected"""
        logger.info(f'Bot is ready! Logged in as {self.user.name}')
        commands_list = [cmd.name for cmd in self.commands]
        logger.info(f"Registered commands: {commands_list}")
        await self.change_presence(activity=discord.Game(name=f"{COMMAND_PREFIX}help"))
        # Reset reconnection attempts and update heartbeat
        self.reconnect_attempts = 0
        self.last_heartbeat = asyncio.get_event_loop().time()

    async def on_command_error(self, ctx, error):
        """Global error handler for commands"""
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"Please wait {error.retry_after:.2f} seconds before using this command again.")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("You don't have permission to use this command.")
        elif isinstance(error, commands.CommandNotFound):
            attempted_command = ctx.message.content.split()[0][1:]
            available_commands = [cmd.name for cmd in self.commands]
            matches = get_close_matches(attempted_command, available_commands, n=1, cutoff=0.6)
            suggestion = matches[0] if matches else available_commands[0]
            await ctx.send(f"Command '{attempted_command}' not found. Did you mean '!{suggestion}'?")
        else:
            logger.error(f"Error occurred: {error}")
            await ctx.send("An error occurred while processing your command.")

    async def on_disconnect(self):
        """Called when the bot disconnects from Discord"""
        logger.warning("Bot disconnected from Discord")
        self.last_heartbeat = None

bot = EducationalBot()

async def main():
    try:
        async with bot:
            await bot.start(os.getenv('DISCORD_TOKEN'))
    except Exception as e:
        logger.critical(f"Failed to start bot: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())