import os
import discord
import ctypes.util
from discord.ext import commands, tasks
from dotenv import load_dotenv
import logging
from utils.logger import setup_logger
from difflib import get_close_matches
import asyncio
import time
from keep_alive import keep_alive
import glob

keep_alive()

# Load environment variables
load_dotenv()

# Setup logging
logger = setup_logger()

# Configure Opus for voice support
try:
    # First try finding opus through ctypes
    opus_path = ctypes.util.find_library('opus')
    if opus_path:
        discord.opus.load_opus(opus_path)
        logger.info(f"Successfully loaded Opus from system path: {opus_path}")
    else:
        # Additional paths to check for Opus
        common_opus_paths = [
            '/usr/lib/libopus.so.0',
            '/usr/lib/x86_64-linux-gnu/libopus.so.0',
            '/usr/local/lib/libopus.so.0',
            '/nix/store/*/lib/libopus.so.0',  # Nix store path
            './libopus.so.0'  # Local directory
        ]

        opus_loaded = False
        for path in common_opus_paths:
            try:
                if '*' in path:
                    # Handle Nix store wildcard path
                    matching_paths = glob.glob(path)
                    for actual_path in matching_paths:
                        try:
                            discord.opus.load_opus(actual_path)
                            logger.info(f"Successfully loaded Opus from Nix store: {actual_path}")
                            opus_loaded = True
                            break
                        except Exception:
                            continue
                else:
                    discord.opus.load_opus(path)
                    logger.info(f"Successfully loaded Opus from alternate path: {path}")
                    opus_loaded = True
                    break
            except Exception as path_error:
                logger.debug(f"Failed to load Opus from {path}: {path_error}")
                continue

        if not opus_loaded:
            logger.warning("Failed to load Opus. Voice functionality may be limited.")
            logger.debug("Attempted paths: " + ", ".join(common_opus_paths))

except Exception as e:
    logger.error(f"Error during Opus initialization: {e}")

# Bot configuration
COMMAND_PREFIX = '!'
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

class EducationalBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=COMMAND_PREFIX,
            intents=intents,
            help_command=None
        )
        self.loaded_extensions = set()
        self._last_connection_check = None
        self._command_cooldowns = {}
        self._command_lock = asyncio.Lock()
        self._processing_commands = set()

    async def setup_hook(self):
        """Setup hook to initialize tasks"""
        self.check_connection.start()

    async def close(self):
        """Cleanup when closing the bot"""
        try:
            self.check_connection.cancel()
            self._command_cooldowns.clear()
            self._processing_commands.clear()
        finally:
            await super().close()

    def _reset_command_cooldowns(self):
        """Reset command cooldowns periodically"""
        current_time = time.time()
        self._command_cooldowns = {
            k: v for k, v in self._command_cooldowns.items()
            if current_time - v < 300  # Keep entries newer than 5 minutes
        }

    @tasks.loop(minutes=1)
    async def check_connection(self):
        try:
            await self.wait_until_ready()
            current_time = time.time()

            if self._last_connection_check:
                time_diff = current_time - self._last_connection_check
                logger.info(f"Connection check - Time since last check: {time_diff:.2f}s")
                if time_diff > 120:  # If more than 2 minutes passed
                    logger.warning("Connection check delayed - Potential connection issues")

            self._last_connection_check = current_time
            logger.info("Connection check - Bot is connected and responsive")

            # Reset command cooldowns every check
            self._reset_command_cooldowns()

        except Exception as e:
            logger.error(f"Connection check failed: {e}")
            try:
                await self.close()
                await asyncio.sleep(5)  # Wait before reconnecting
                await self.start(os.getenv('DISCORD_TOKEN'))
            except Exception as reconnect_error:
                logger.error(f"Reconnection attempt failed: {reconnect_error}")

    async def process_commands(self, message):
        """Override to add command execution tracking"""
        if message.author.bot:
            return

        ctx = await self.get_context(message)
        if ctx.command is None:
            return

        command_key = f"{ctx.author.id}:{ctx.command.name}"
        current_time = time.time()

        # Use lock to prevent race conditions
        async with self._command_lock:
            # Check if command is already being processed
            if command_key in self._processing_commands:
                logger.debug(f"Duplicate command prevented: {command_key}")
                return

            # Check cooldown
            if command_key in self._command_cooldowns:
                last_use = self._command_cooldowns[command_key]
                if current_time - last_use < 1.0:  # 1 second cooldown
                    return

            # Mark command as being processed
            self._processing_commands.add(command_key)

        try:
            self._command_cooldowns[command_key] = current_time
            await self.invoke(ctx)
        finally:
            # Always remove from processing set when done
            self._processing_commands.remove(command_key)

# Create bot instance
bot = EducationalBot()

# Load cogs
async def load_extensions():
    """Load bot extensions"""
    if not bot.loaded_extensions:  # Only load if not already loaded
        extensions = [
            'cogs.education_manager_new',  # Primary education cog
            'cogs.admin_commands',  # Admin commands
            'cogs.ticket_manager',  # Ticket system
            'cogs.music_commands',  # Music commands with improved audio quality
            'cogs.subject_curriculum_new'  # Subject curriculum management
        ]

        for extension in extensions:
            try:
                await bot.load_extension(extension)
                bot.loaded_extensions.add(extension)
                logger.info(f"Successfully loaded extension: {extension}")
            except Exception as e:
                logger.error(f"Failed to load extension {extension}: {e}")
                raise  # Re-raise to prevent partial loading

        logger.info("Successfully loaded all extensions")

@bot.event
async def on_ready():
    logger.info(f'Bot is ready! Logged in as {bot.user.name}')
    commands_list = [cmd.name for cmd in bot.commands]
    logger.info(f"Registered commands: {commands_list}")
    await bot.change_presence(activity=discord.Game(name=f"{COMMAND_PREFIX}help"))

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"Please wait {error.retry_after:.2f} seconds before using this command again.")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have permission to use this command.")
    elif isinstance(error, commands.CommandNotFound):
        attempted_command = ctx.message.content.split()[0][1:]
        available_commands = [cmd.name for cmd in bot.commands]
        matches = get_close_matches(attempted_command, available_commands, n=1, cutoff=0.6)
        suggestion = matches[0] if matches else available_commands[0]
        await ctx.send(f"Command '{attempted_command}' not found. Did you mean '!{suggestion}'?")
    elif "Section not found" in str(error):
        await ctx.send("❌ The specified section or category was not found. Please check available sections using !subjects or !chapters11/!chapters12 commands.")
    else:
        logger.error(f"Error occurred: {error}")
        await ctx.send("An error occurred while processing your command.")

async def main():
    try:
        async with bot:
            await load_extensions()
            token = os.getenv('DISCORD_TOKEN')
            if not token:
                logger.error("Discord token not found in environment variables")
                return
            await bot.start(token)
    except Exception as e:
        logger.error(f"Main loop error: {e}")
        await asyncio.sleep(5)  # Wait before retry
        await main()  # Retry connection

if __name__ == "__main__":
    asyncio.run(main())