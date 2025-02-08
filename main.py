import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import logging
from utils.logger import setup_logger

# Load environment variables
load_dotenv()

# Setup logging
logger = setup_logger()

# Bot configuration
COMMAND_PREFIX = '!'
intents = discord.Intents.default()
intents.message_content = True  # Required for reading message content
intents.guilds = True          # Required for guild/server information

bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)

# Load cogs
async def load_extensions():
    await bot.load_extension('cogs.education')
    await bot.load_extension('cogs.admin')

@bot.event
async def on_ready():
    logger.info(f'Bot is ready! Logged in as {bot.user.name}')
    await bot.change_presence(activity=discord.Game(name=f"{COMMAND_PREFIX}help"))

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"Please wait {error.retry_after:.2f} seconds before using this command again.")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have permission to use this command.")
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