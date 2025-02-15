import os
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
import logging
from utils.logger import setup_logger
import asyncio
from keep_alive import keep_alive

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
intents.messages = True  # Required for message commands

class EducationalBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=COMMAND_PREFIX,
            intents=intents,
            help_command=None  # Disable default help command
        )
        self.initial_extensions = [
            'cogs.education_manager_new',
            'cogs.admin_core',
            'cogs.subject_curriculum_new',
            'cogs.music_commands_enhanced',  # Music cog
            'cogs.staff_commands',
            'cogs.ticket_manager',
            'cogs.invite_manager',  # Added invite manager cog
            'cogs.ai_chat_commands'  # Using new AI chat commands
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

    async def on_ready(self):
        """Called when the bot is ready and connected"""
        logger.info(f'Bot is ready! Logged in as {self.user.name}')
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
        # Keep the web server alive
        keep_alive()

        # Initialize bot
        bot = EducationalBot()

        # Get token
        token = os.getenv('DISCORD_TOKEN')
        if not token:
            logger.error("No Discord token found in environment variables!")
            return

        logger.info("Starting bot...")
        await bot.start(token)
    except Exception as e:
        logger.error(f"Error starting bot: {str(e)}")
        logger.exception(e)

if __name__ == "__main__":
    asyncio.run(main())