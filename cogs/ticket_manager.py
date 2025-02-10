
import discord
from discord.ext import commands
import asyncio
from discord import ButtonStyle, SelectOption
from discord.ui import Button, View

class TicketSelect(discord.ui.Select):
    def __init__(self):
        options = [
            SelectOption(label="Support Ticket", description="Get help with any issues", emoji="🎫", value="support"),
            SelectOption(label="Claim Reward", description="Claim your rewards and prizes", emoji="🎁", value="reward")
        ]
        super().__init__(placeholder="Choose ticket type...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        view = self.view
        if isinstance(view, TicketView):
            await view.create_ticket_callback(interaction, self.values[0])

class TicketView(View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot
        self.add_item(TicketSelect())
    
    async def create_ticket_callback(self, interaction: discord.Interaction, ticket_type: str):
        await interaction.response.defer(ephemeral=True)
        
        # Check if user already has a ticket
        cog = self.bot.get_cog('TicketManager')
        if interaction.user.id in cog.active_tickets:
            await interaction.followup.send("❌ You already have an active ticket!", ephemeral=True)
            return
            
        # Create ticket channel
        guild = interaction.guild
        category = discord.utils.get(guild.categories, name='Tickets')
        
        if category is None:
            category = await guild.create_category('Tickets')
            
        channel_name = f'ticket-{interaction.user.name}'
        
        # Set permissions
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        
        # Create the ticket channel
        ticket_channel = await category.create_text_channel(
            name=channel_name,
            overwrites=overwrites
        )
        
        cog.active_tickets[interaction.user.id] = ticket_channel.id
        
        # Create embed for the ticket channel
        embed = discord.Embed(
            title=f"{'🎫 Support Request' if ticket_type == 'support' else '🎁 Reward Claim Request'}",
            description=f"👋 **Welcome {interaction.user.mention}!**\n\n🔹 Your ticket has been created successfully.\n🔹 **Please wait until our support team assists you shortly.**\n🔹 Describe your request in detail while waiting.",
            color=discord.Color.brand_green() if ticket_type == 'support' else discord.Color.gold()
        )
        embed.add_field(
            name="👤 User Information",
            value=f"**Requestor:** {interaction.user.mention}\n**ID:** {interaction.user.id}",
            inline=True
        )
        embed.add_field(
            name="🎫 Ticket Details",
            value=f"**Type:** {'Support Assistance' if ticket_type == 'support' else 'Reward Claim'}\n**Status:** Active",
            inline=True
        )
        embed.set_footer(text="Use the 🔒 Close Ticket button when your request is resolved")

        class CloseButton(discord.ui.Button):
            def __init__(self):
                super().__init__(style=discord.ButtonStyle.danger, label="Close Ticket", emoji="🔒")

            async def callback(self, interaction: discord.Interaction):
                await interaction.response.defer()
                cog = interaction.client.get_cog('TicketManager')
                ctx = await interaction.client.get_context(interaction.message)
                await cog.close_ticket(ctx)

        view = discord.ui.View(timeout=None)
        view.add_item(CloseButton())
        
        await ticket_channel.send(f"{interaction.user.mention}", embed=embed, view=view)
        await interaction.followup.send(f"✅ Ticket created! Please check {ticket_channel.mention}", ephemeral=True)

class TicketManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_tickets = {}
        self.ticket_channel_id = None

    @commands.command(name='setuptickets')
    @commands.has_permissions(administrator=True)
    async def setup_tickets(self, ctx, channel: discord.TextChannel = None):
        """Set up the ticket system in a specific channel"""
        channel = channel or ctx.guild.get_channel(1338330187632476291)
        if not channel:
            await ctx.send("❌ Channel not found!")
            return
            
        self.ticket_channel_id = channel.id
        
        # Create the ticket message
        embed = discord.Embed(
            title="🎫 Ticket System",
            description="Click on the button corresponding to the type of ticket you wish to open!",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="📋 Available Ticket Types",
            value="🎫 **Support Ticket**\n• Get help with any issues\n• Ask questions\n• Report problems\n\n"
                  "🎁 **Claim Reward**\n• Claim your rewards\n• Redeem prizes\n• Special requests",
            inline=False
        )
        embed.add_field(
            name="💡 How it works",
            value="1️⃣ Click the appropriate button below\n"
                  "2️⃣ A private channel will be created\n"
                  "3️⃣ Describe your request there\n"
                  "4️⃣ Staff will assist you shortly",
            inline=False
        )
        embed.set_footer(text="Choose your ticket type below!")
        
        # Send message with button
        view = TicketView(self.bot)
        await channel.send(embed=embed, view=view)

    @commands.command(name='close')
    async def close_ticket(self, ctx):
        """Close a support ticket"""
        if not isinstance(ctx.channel, discord.TextChannel) or 'ticket-' not in ctx.channel.name:
            await ctx.send("❌ This command can only be used in ticket channels!")
            return

        close_embed = discord.Embed(
            title="🔒 Closing Ticket",
            description="This ticket will be closed in 5 seconds...",
            color=discord.Color.orange()
        )
        await ctx.send(embed=close_embed)
        await asyncio.sleep(5)
        
        # Remove from active tickets
        user_id = next((k for k, v in self.active_tickets.items() if v == ctx.channel.id), None)
        if user_id:
            del self.active_tickets[user_id]

        await ctx.channel.delete()

async def setup(bot):
    await bot.add_cog(TicketManager(bot))
