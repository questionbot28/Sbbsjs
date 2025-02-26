import discord
from discord.ext import commands
import asyncio
from typing import Dict, List, Optional
import logging
from discord.ui import View, Button, button

class HelpMenuView(View):
    def __init__(self, cog, timeout=60):
        super().__init__(timeout=timeout)
        self.cog = cog
        self.add_category_buttons()

    def add_category_buttons(self):
        categories = {
            "education": ("📚", discord.ButtonStyle.primary),
            "music": ("🎵", discord.ButtonStyle.success),
            "tickets": ("🎫", discord.ButtonStyle.secondary),
            "invites": ("📊", discord.ButtonStyle.primary),
            "ai": ("🤖", discord.ButtonStyle.success)
        }

        for category, (emoji, style) in categories.items():
            button = Button(
                style=style,
                label=category.title(),
                emoji=emoji,
                custom_id=f"help_{category}"
            )
            button.callback = lambda interaction, cat=category: self.cog.handle_category_select(interaction, cat)
            self.add_item(button)

class InteractiveHelp(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger('discord_bot')
        self.active_menus: Dict[int, discord.Message] = {}
        self.tooltip_frames = [
            "⠋ Loading...", "⠙ Loading...", "⠹ Loading...",
            "⠸ Loading...", "⠼ Loading...", "⠴ Loading...",
            "⠦ Loading...", "⠧ Loading...", "⠇ Loading...",
            "⠏ Loading..."
        ]

    @commands.command(name='help2', description='Shows the new interactive help menu')
    async def interactive_help(self, ctx):
        """Display the interactive help menu with animated tooltips"""
        try:
            embed = discord.Embed(
                title="✨ Interactive Command Center ✨",
                description="Welcome to the enhanced help menu! Click the buttons below to explore different command categories.",
                color=discord.Color.blue()
            )

            categories = {
                "📚 Education": "Master your studies with Class 11-12 questions",
                "🎵 Music": "Enjoy music with advanced playback controls",
                "🎫 Tickets": "Get support through our ticket system",
                "📊 Invites": "Track and manage server invitations",
                "🤖 AI Chat": "Interact with our AI assistant"
            }

            for category, desc in categories.items():
                embed.add_field(
                    name=f"{category}",
                    value=f"```ansi\n[2;34m{desc}[0m```",
                    inline=False
                )

            embed.set_footer(text="✨ Click a button below to explore commands!")
            view = HelpMenuView(self)
            menu_msg = await ctx.send(embed=embed, view=view)
            self.active_menus[ctx.author.id] = menu_msg
            await self._show_tooltip(menu_msg, "🎯 Select a category using the buttons below!")

        except Exception as e:
            self.logger.error(f"Error showing interactive help: {e}")
            await ctx.send("❌ An error occurred while displaying the help menu.")

    async def handle_category_select(self, interaction: discord.Interaction, category: str):
        """Handle button clicks for category selection"""
        try:
            commands = {
                "education": {
                    "!11": "Get Class 11 Questions",
                    "!12": "Get Class 12 Questions",
                    "!subjects": "List All Subjects",
                    "!chapters11": "View Class 11 Chapters",
                    "!chapters12": "View Class 12 Chapters"
                },
                "music": {
                    "!play": "Play a song or playlist",
                    "!pause": "Pause current song",
                    "!resume": "Resume playback",
                    "!skip": "Skip to next song",
                    "!queue": "View song queue"
                },
                "invites": {
                    "!invites": "View your invite statistics",
                    "!invite-stats": "Detailed invite analytics",
                    "!invite-history": "Check invite history",
                    "!invite-leaderboard": "Server invite rankings"
                },
                "tickets": {
                    "!ticket": "Create support ticket",
                    "!close": "Close active ticket",
                    "!add": "Add user to ticket",
                    "!remove": "Remove from ticket"
                },
                "ai": {
                    "!ask": "Ask AI a question",
                    "!chat": "Start AI conversation",
                    "!summary": "Generate AI summary",
                    "!explain": "Get AI explanation"
                }
            }

            embed = discord.Embed(
                title=f"📖 {category.title()} Commands",
                description=f"Explore the {category.title()} category commands below:",
                color=discord.Color.blue()
            )

            for cmd, desc in commands[category].items():
                embed.add_field(
                    name=cmd,
                    value=f"```ansi\n[2;32m{desc}[0m```",
                    inline=False
                )

            embed.set_footer(text=f"✨ Browsing {category.title()} commands")
            view = HelpMenuView(self)  # Create new view for new embed
            await interaction.response.edit_message(embed=embed, view=view)

            if interaction.message.id in self.active_menus.values():
                await self._show_tooltip(interaction.message, f"✨ Showing {category.title()} commands!")

        except Exception as e:
            self.logger.error(f"Error handling category selection: {e}")
            await interaction.response.send_message("❌ An error occurred while showing category commands.", ephemeral=True)

    async def _show_tooltip(self, message: discord.Message, text: str, duration: int = 3):
        """Display an animated tooltip"""
        try:
            embed = message.embeds[0]
            original_footer = embed.footer.text

            for _ in range(2):  # Run animation twice
                for frame in self.tooltip_frames:
                    embed.set_footer(text=f"{frame} {text}")
                    await message.edit(embed=embed)
                    await asyncio.sleep(0.2)

            embed.set_footer(text=original_footer)
            await message.edit(embed=embed)

        except Exception as e:
            self.logger.error(f"Error showing tooltip: {e}")

async def setup(bot):
    await bot.add_cog(InteractiveHelp(bot))