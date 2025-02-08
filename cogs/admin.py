import discord
from discord.ext import commands
import logging

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger('discord_bot')

    @commands.command(name='ping')
    async def ping(self, ctx):
        """Check bot's latency"""
        latency = round(self.bot.latency * 1000)
        await ctx.send(f'Pong! Latency: {latency}ms')

    @commands.command(name='stats')
    @commands.has_permissions(administrator=True)
    async def stats(self, ctx):
        """Show bot statistics"""
        embed = discord.Embed(
            title="Bot Statistics",
            color=discord.Color.blue()
        )
        embed.add_field(name="Servers", value=str(len(self.bot.guilds)))
        embed.add_field(name="Users", value=str(sum(guild.member_count for guild in self.bot.guilds)))
        embed.add_field(name="Commands", value=str(len(self.bot.commands)))
        await ctx.send(embed=embed)

    @commands.command(name='clear')
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int = 5):
        """Clear specified number of messages"""
        if amount > 100:
            await ctx.send("Cannot delete more than 100 messages at once.")
            return
        
        deleted = await ctx.channel.purge(limit=amount + 1)
        await ctx.send(f"Deleted {len(deleted)-1} messages.", delete_after=5)

async def setup(bot):
    await bot.add_cog(Admin(bot))
