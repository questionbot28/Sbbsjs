import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import logging
from utils.logger import setup_logger
from difflib import get_close_matches  # Add this import

# Load environment variables
load_dotenv()

# Setup logging
logger = setup_logger()

# Bot configuration
COMMAND_PREFIX = '!'
intents = discord.Intents.default()
intents.message_content = True  # Required for reading message content
intents.guilds = True          # Required for guild/server information

# Create bot instance with help_command=None to disable default help command
bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents, help_command=None)

# Load cogs
async def load_extensions():
    try:
        await bot.load_extension('cogs.education')
        await bot.load_extension('cogs.admin')
        logger.info("Successfully loaded all extensions")
    except Exception as e:
        logger.error(f"Failed to load extensions: {e}")

@bot.event
async def on_ready():
    logger.info(f'Bot is ready! Logged in as {bot.user.name}')
    # List all registered commands
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
        # Get the attempted command
        attempted_command = ctx.message.content.split()[0][1:]  # Remove the prefix
        available_commands = [cmd.name for cmd in bot.commands]

        # Find closest matching command using get_close_matches
        matches = get_close_matches(attempted_command, available_commands, n=1, cutoff=0.6)
        suggestion = matches[0] if matches else available_commands[0]

        await ctx.send(f"Command '{attempted_command}' not found. Did you mean '!{suggestion}'?")
    else:
        logger.error(f"Error occurred: {error}")
        await ctx.send("An error occurred while processing your command.")

async def main():
    async with bot:
        await load_extensions()
        await bot.start(os.getenv('DISCORD_TOKEN'))

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())