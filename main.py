import os
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
import logging
from utils.logger import setup_logger
import asyncio
from keep_alive import keep_alive  # Using keep_alive instead of server

# Load environment variables with override to ensure Glitch env vars take precedence
load_dotenv(override=True)  

# Setup logging
logger = setup_logger()

# Bot configuration
COMMAND_PREFIX = '!'
intents = discord.Intents.default()
intents.message_content = True  # Required for detecting commands
intents.guilds = True  # Required for guild-related functionality
intents.voice_states = True  # Required for voice features
intents.members = True  # Needed for on_member_join event

async def initialize_server():
    """Initialize the Flask server and verify it's running"""
    try:
        logger.info("Starting keep_alive server...")
        keep_alive()

        # Give the server more time to start
        logger.info("Waiting for Flask server to initialize...")
        await asyncio.sleep(5)  # Increased from 2 to 5 seconds

        # Test server accessibility with retries
        import requests
        from requests.exceptions import RequestException

        retries = 3
        while retries > 0:
            try:
                logger.info("Attempting to connect to Flask server...")
                response = requests.get('http://0.0.0.0:5000/health')
                if response.status_code == 200:
                    logger.info("Flask server is running and accessible")
                    server_status = response.json()
                    logger.info(f"Server status: {server_status}")
                    break
                else:
                    logger.warning(f"Server health check failed with status code: {response.status_code}")
            except RequestException as e:
                logger.warning(f"Failed to connect to Flask server (attempt {4-retries}/3): {e}")
                if retries > 1:
                    logger.info("Waiting before retry...")
                    await asyncio.sleep(2)
            retries -= 1

        if retries == 0:
            logger.error("Failed to verify Flask server status after multiple attempts")
            raise Exception("Could not verify Flask server status")

    except Exception as e:
        logger.error(f"Error initializing server: {e}")
        raise

class EducationalBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=COMMAND_PREFIX,
            intents=intents,
            help_command=None  # Disable default help command
        )
        self.initial_extensions = [
            'cogs.ai_chat_enhanced',  # Using enhanced AI chat with Gemini
            'cogs.admin_core',
            'cogs.education_manager_new',
            'cogs.music_commands_enhanced',
            'cogs.staff_commands',
            'cogs.ticket_manager',
            'cogs.invite_manager',
            'cogs.subjects_viewer',
            'cogs.interactive_help',
            'cogs.command_explainer',
            'cogs.achievements',
            'cogs.flashcards',
            'cogs.learning_assistant',
        ]
        self.logger = logger

    async def setup_hook(self):
        """Initial setup and load extensions"""
        logger.info("Starting bot initialization...")
        logger.info("Loading extensions...")

        for extension in self.initial_extensions:
            try:
                logger.info(f"Loading extension: {extension}")
                await self.load_extension(extension)
                logger.info(f"Successfully loaded extension: {extension}")
            except Exception as e:
                logger.error(f"Failed to load extension {extension}: {str(e)}")
                logger.exception(e)
                # Log additional details about the error
                import traceback
                logger.error(f"Full traceback for {extension}:")
                logger.error(traceback.format_exc())

    async def on_ready(self):
        """Called when the bot is ready and connected"""
        logger.info(f'Bot is ready! Logged in as {self.user.name}')
        # Log all registered commands
        commands_list = [cmd.name for cmd in self.commands]
        logger.info(f"Registered commands: {', '.join(commands_list)}")

        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.listening,
                name=f"{COMMAND_PREFIX}help"
            )
        )

    async def on_message(self, message):
        """Enhanced message handling with debug logging"""
        if message.author.bot:
            return

        logger.debug(f"Message received from {message.author}: {message.content}")
        if message.content.startswith(COMMAND_PREFIX):
            logger.info(f"Command detected: {message.content}")

        try:
            await self.process_commands(message)
        except Exception as e:
            logger.error(f"Error processing command: {str(e)}")
            logger.exception(e)

    async def on_command_error(self, ctx, error):
        """Enhanced error handling for commands"""
        if isinstance(error, commands.CommandNotFound):
            await ctx.send(f"❌ Command not found. Use {COMMAND_PREFIX}help to see available commands.")
            logger.warning(f"Command not found: {ctx.message.content}")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You don't have permission to use this command.")
            logger.warning(f"Missing permissions for {ctx.author}: {error}")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"❌ Missing required argument: {error.param.name}")
            logger.warning(f"Missing argument in command: {ctx.message.content}")
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"⏳ Please wait {error.retry_after:.1f}s before using this command again.")
            logger.info(f"Command on cooldown for {ctx.author}: {ctx.command.name}")
        else:
            logger.error(f"Unhandled command error: {error}")
            await ctx.send("❌ An error occurred while processing your command.")
            logger.exception(error)

async def main():
    try:
        # Initialize Flask server first
        await initialize_server()

        # Initialize bot
        bot = EducationalBot()

        # Get token with better error handling
        token = os.getenv('DISCORD_TOKEN')
        if not token:
            logger.error("No Discord token found in environment variables!")
            logger.info("Please make sure DISCORD_TOKEN is set in your .env file")
            return

        logger.info("Starting bot...")
        await bot.start(token)

    except discord.LoginFailure as e:
        logger.error(f"Failed to log in: Invalid token. Please check your DISCORD_TOKEN in .env")
        logger.exception(e)
    except Exception as e:
        logger.error(f"Error starting bot: {str(e)}")
        logger.exception(e)

if __name__ == "__main__":
    asyncio.run(main())