
import discord
from discord.ext import commands
import asyncio

class TicketManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_tickets = {}

    @commands.command(name='ticket')
    async def create_ticket(self, ctx):
        """Create a support ticket"""
        # Check if user already has an active ticket
        if ctx.author.id in self.active_tickets:
            await ctx.send("❌ You already have an active ticket!")
            return

        # Create ticket channel
        guild = ctx.guild
        category = discord.utils.get(guild.categories, name='Tickets')
        
        if category is None:
            # Create ticket category if it doesn't exist
            category = await guild.create_category('Tickets')

        # Create channel name
        channel_name = f'ticket-{ctx.author.name}-{ctx.author.discriminator}'
        
        # Create permissions
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            ctx.author: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        # Create ticket channel
        ticket_channel = await category.create_text_channel(
            name=channel_name,
            overwrites=overwrites
        )

        self.active_tickets[ctx.author.id] = ticket_channel.id

        # Send initial message in ticket channel
        embed = discord.Embed(
            title="🎫 Support Ticket",
            description="Thank you for creating a ticket! Support staff will be with you shortly.",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="Commands",
            value="Use `!close` to close this ticket when resolved.",
            inline=False
        )
        await ticket_channel.send(embed=embed)
        await ctx.send(f"✅ Ticket created! Please check {ticket_channel.mention}")

    @commands.command(name='close')
    async def close_ticket(self, ctx):
        """Close a support ticket"""
        if not isinstance(ctx.channel, discord.TextChannel) or 'ticket-' not in ctx.channel.name:
            await ctx.send("❌ This command can only be used in ticket channels!")
            return

        # Send closing message
        await ctx.send("🔒 Closing ticket in 5 seconds...")
        await asyncio.sleep(5)
        
        # Remove from active tickets
        user_id = next((k for k, v in self.active_tickets.items() if v == ctx.channel.id), None)
        if user_id:
            del self.active_tickets[user_id]

        # Delete the channel
        await ctx.channel.delete()

async def setup(bot):
    await bot.add_cog(TicketManager(bot))
