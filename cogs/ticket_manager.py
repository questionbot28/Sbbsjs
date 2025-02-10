
import discord
from discord.ext import commands
import asyncio
from discord import ButtonStyle, SelectOption
from discord.ui import Button, View

class TicketSelect(discord.ui.Select):
    def __init__(self):
        options = [
            SelectOption(
                label="Academic Support",
                description="Get help with your studies",
                emoji="📚",
                value="support"
            ),
            SelectOption(
                label="Resource Access",
                description="Access study materials and guides",
                emoji="📖",
                value="resource"
            )
        ]
        super().__init__(
            placeholder="Choose support type...",
            min_values=1,
            max_values=1,
            options=options
        )

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
        
        # Get ticket manager cog
        ticket_manager = self.bot.get_cog('TicketManager')
        if interaction.user.id in ticket_manager.active_tickets:
            await interaction.followup.send("❌ You already have an active ticket!", ephemeral=True)
            return

        # Create ticket channel
        guild = interaction.guild
        category = discord.utils.get(guild.categories, name='Tickets')
        
        if category is None:
            category = await guild.create_category('Tickets')

        channel_name = f'ticket-{interaction.user.name}'
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        ticket_channel = await category.create_text_channel(
            name=channel_name,
            overwrites=overwrites
        )

        ticket_manager.active_tickets[interaction.user.id] = ticket_channel.id

        # Create welcome embed
        welcome_message = (
            "┏━━━━━━━━━━ 🎟️ EduSphere Support ━━━━━━━━━━┓\n"
            f"👋 Hello, {interaction.user.mention}!\n"
            "Your educational support ticket has been created.\n"
            "An EduSphere advisor will assist you shortly.\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛"
        )

        ticket_details = (
            "┏━━━━━━━━━━ 📜 Ticket Details ━━━━━━━━━━┓\n"
            f"🔹 User: {interaction.user.mention}\n"
            f"🔹 ID: {interaction.user.id}\n"
            f"🔹 Type: {'Academic Support' if ticket_type == 'support' else 'Resource Access'}\n"
            "🔹 Status: 🟢 Active\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛"
        )

        instructions = (
            "┏━━━━━━━━━━ ℹ️ Instructions ━━━━━━━━━━┓\n"
            "✅ Clearly explain your academic query or request.\n"
            "✅ Wait for an EduSphere advisor to respond.\n"
            "✅ Click the 🔒 button when your query is resolved.\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛"
        )

        embed = discord.Embed(
            description=f"{welcome_message}\n\n{ticket_details}\n\n{instructions}",
            color=discord.Color.blue()
        )
        embed.set_footer(text="🔔 An EduSphere advisor will be with you shortly!")

        class CloseButton(discord.ui.Button):
            def __init__(self):
                super().__init__(style=discord.ButtonStyle.danger, label="Close Ticket", emoji="🔒")

            async def callback(self, interaction: discord.Interaction):
                await interaction.response.defer()
                ticket_manager = interaction.client.get_cog('TicketManager')
                ctx = await interaction.client.get_context(interaction.message)
                await ticket_manager.close_ticket(ctx)

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
        channel = channel or ctx.channel

        # Create the ticket message with new formatting
        embed = discord.Embed(
            title="🎓 EduSphere Support Center",
            description="📚 **Welcome to Your EduSphere Support Hub**\n\nGet assistance with your studies and access educational resources!",
            color=discord.Color.blue()
        )
        ticket_types = (
            "🎫 **Academic Support**\n\n"
            "🔹 Get help with study materials and concepts\n"
            "🔹 Ask questions about specific topics\n"
            "🔹 Request additional learning resources\n\n"
            "🎁 **Resource Access**\n\n"
            "📘 Access study materials and guides\n"
            "📝 Request practice questions and solutions\n"
            "📚 Get help with subject-specific queries\n\n"
            "⚠️ **Note:** Please be specific with your academic queries.\n\n"
            "👨‍🏫 Our EduSphere advisors will assist you promptly!"
        )
        embed.add_field(
            name="",
            value=ticket_types,
            inline=False
        )
        embed.add_field(
            name="💡 How it works",
            value="1️⃣ Select your request type below\n"
                  "2️⃣ A private support channel will be created\n"
                  "3️⃣ Describe your academic query clearly\n"
                  "4️⃣ An EduSphere advisor will assist you",
            inline=False
        )
        embed.set_footer(text="Select your support type below! 📚")

        # Send message with view
        view = TicketView(self.bot)
        await channel.send(embed=embed, view=view)

    @commands.command(name='close')
    async def close_ticket(self, ctx):
        """Close a support ticket"""
        if not isinstance(ctx.channel, discord.TextChannel) or 'ticket-' not in ctx.channel.name:
            await ctx.send("❌ This command can only be used in ticket channels!")
            return

        close_embed = discord.Embed(
            title="🔒 Closing EduSphere Support Ticket",
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
