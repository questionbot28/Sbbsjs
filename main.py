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

        # Give the server a moment to start
        await asyncio.sleep(2)

        # Test server accessibility
        import requests
        try:
            response = requests.get('http://0.0.0.0:5000/health')
            if response.status_code == 200:
                logger.info("Flask server is running and accessible")
                server_status = response.json()
                logger.info(f"Server status: {server_status}")
            else:
                logger.error(f"Server health check failed with status code: {response.status_code}")
        except requests.RequestException as e:
            logger.error(f"Failed to connect to Flask server: {e}")

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
            'cogs.education_manager_new',
            'cogs.admin_core',
            'cogs.subject_curriculum_new',
            'cogs.music_commands_enhanced',  # Using enhanced music commands
            'cogs.staff_commands',
            'cogs.ticket_manager',
            'cogs.invite_manager',
            'cogs.ai_chat_enhanced',  # Using enhanced AI chat
            'cogs.admin_commands',  # Additional admin commands
            'cogs.subjects_viewer',  # Subject viewing functionality
            'cogs.interactive_help',  # New interactive help system
            'cogs.command_explainer',  # Command explanation generator
            'cogs.achievements',  # Achievement system
            'cogs.flashcards',  # New flashcard system
            'cogs.learning_assistant',  # New AI-powered learning assistant
        ]
        self.logger = logger
        self.welcome_channel_id = 1337410430699569232
        self.help_channel_id = 1337414736802742393
        self.roles_channel_id = 1337427674347339786

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

    async def on_member_join(self, member):
        """Send welcome message when a new member joins"""
        try:
            welcome_channel = self.get_channel(self.welcome_channel_id)
            if welcome_channel:
                welcome_message = (
                    f"🎉 Welcome, {member.mention}! Glad to have you in EduSphere – "
                    f"Learn, Share, Grow! 📚✨\n\n"
                    f"🤝 Need help? Ask in <#{self.help_channel_id}>\n"
                    f"🔰 Get your class role in <#{self.roles_channel_id}>\n\n"
                    f"Say hi and introduce yourself! 🚀"
                )
                await welcome_channel.send(welcome_message)
                self.logger.info(f"Sent welcome message to {member.name} in {welcome_channel.name}")
        except Exception as e:
            self.logger.error(f"Error sending welcome message: {str(e)}")
            self.logger.exception(e)

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
        # Add debug logging for token presence
        logger.info("Token exists and attempting to connect...")
        await bot.start(token)

    except discord.LoginFailure as e:
        logger.error(f"Failed to log in: Invalid token. Please check your DISCORD_TOKEN in .env")
        logger.exception(e)
    except Exception as e:
        logger.error(f"Error starting bot: {str(e)}")
        logger.exception(e)

if __name__ == "__main__":
    asyncio.run(main())