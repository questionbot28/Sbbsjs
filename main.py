import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import logging
from utils.logger import setup_logger
import asyncio
# Skip Flask server for now
# from keep_alive import keep_alive, is_port_available
# import time

# Load environment variables
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

class EducationalBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=COMMAND_PREFIX,
            intents=intents,
            help_command=None  # Disable default help command
        )
        self.logger = logger
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
            'cogs.voice_commands',  # Added voice commands cog
            'cogs.natural_conversation',  # Added natural conversation cog
        ]

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

    async def on_ready(self):
        """Called when the bot is ready and connected"""
        logger.info(f'Bot is ready! Logged in as {self.user.name}')

        # Enhanced command logging
        all_commands = {}
        for command in self.commands:
            cog_name = command.cog.qualified_name if command.cog else 'No Category'
            if cog_name not in all_commands:
                all_commands[cog_name] = []
            all_commands[cog_name].append(command.name)

        # Log commands by category
        logger.info("=== Registered Commands ===")
        for category, commands in all_commands.items():
            logger.info(f"{category}: {', '.join(commands)}")
        logger.info("=========================")

        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.listening,
                name=f"{COMMAND_PREFIX}help"
            )
        )

async def main():
    try:
        # Skip Flask server initialization for now
        # logger.info("Starting Flask server initialization...")
        # await initialize_server()

        # Initialize bot
        bot = EducationalBot()

        # Get token
        token = os.getenv('DISCORD_TOKEN')
        if not token:
            logger.error("No Discord token found in environment variables!")
            logger.info("Please make sure DISCORD_TOKEN is set in your .env file")
            return

        logger.info("Starting bot...")
        await bot.start(token)

    except Exception as e:
        logger.error(f"Error starting bot: {str(e)}")
        logger.exception(e)

if __name__ == "__main__":
    asyncio.run(main())