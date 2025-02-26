import discord
from discord.ext import commands
import asyncio
from typing import Dict, List, Optional
import logging

class InteractiveHelp(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger('discord_bot')
        # Store active help menus
        self.active_menus: Dict[int, discord.Message] = {}
        # Animation frames for tooltips
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
            # Create initial embed
            embed = discord.Embed(
                title="🎮 Interactive Command Help",
                description="Welcome to the interactive help menu! Click the buttons below to explore different command categories.",
                color=discord.Color.blue()
            )

            # Add initial categories
            categories = {
                "📚 Education": "Class 11-12 study commands",
                "🎵 Music": "Music playback controls",
                "🎫 Tickets": "Support ticket system",
                "📊 Invites": "Invitation tracking system",
                "🤖 AI Chat": "AI conversation commands"
            }

            for category, desc in categories.items():
                embed.add_field(
                    name=f"{category} Commands",
                    value=f"```{desc}\nClick for details!```",
                    inline=False
                )

            embed.set_footer(text="✨ Click on a category to see detailed commands!")

            # Send initial embed
            menu_msg = await ctx.send(embed=embed)
            self.active_menus[ctx.author.id] = menu_msg

            # Add animated tooltip
            await self._show_tooltip(menu_msg, "🎯 Select a category to explore commands!")

        except Exception as e:
            self.logger.error(f"Error showing interactive help: {e}")
            await ctx.send("❌ An error occurred while displaying the help menu.")

    async def _show_tooltip(self, message: discord.Message, text: str, duration: int = 3):
        """Display an animated tooltip"""
        try:
            embed = message.embeds[0]
            original_footer = embed.footer.text

            # Animate the tooltip
            for _ in range(2):  # Run animation twice
                for frame in self.tooltip_frames:
                    embed.set_footer(text=f"{frame} {text}")
                    await message.edit(embed=embed)
                    await asyncio.sleep(0.2)

            # Restore original footer
            embed.set_footer(text=original_footer)
            await message.edit(embed=embed)

        except Exception as e:
            self.logger.error(f"Error showing tooltip: {e}")

    @commands.Cog.listener()
    async def on_message(self, message):
        """Handle interactive responses"""
        if message.author.bot:
            return

        # Check if user has an active help menu
        if message.author.id in self.active_menus:
            original_msg = self.active_menus[message.author.id]

            # Check if message is a category name
            content = message.content.lower()
            if any(cat.lower() in content for cat in ["education", "music", "tickets", "invites", "ai"]):
                await self._show_category_commands(message, content, original_msg)

    async def _show_category_commands(self, message, category: str, original_msg: discord.Message):
        """Show commands for selected category"""
        try:
            embed = original_msg.embeds[0]

            # Define command details for each category
            commands = {
                "education": {
                    "!11": "Get Class 11 Questions",
                    "!12": "Get Class 12 Questions",
                    "!subjects": "List All Subjects",
                    "!chapters11": "View Class 11 Chapters",
                    "!chapters12": "View Class 12 Chapters"
                },
                "music": {
                    "!play": "Play a song",
                    "!pause": "Pause current song",
                    "!resume": "Resume playback",
                    "!skip": "Skip current song",
                    "!queue": "View song queue"
                },
                "invites": {
                    "!invites": "See your invite stats",
                    "!invite-stats": "View detailed invite statistics",
                    "!invite-history": "View invite history",
                    "!invite-leaderboard": "Check the server's invite rankings"
                },
                "tickets": {
                    "!ticket": "Create a support ticket",
                    "!close": "Close current ticket",
                    "!add": "Add user to ticket",
                    "!remove": "Remove user from ticket"
                },
                "ai": {
                    "!ask": "Ask AI a question",
                    "!chat": "Start AI conversation",
                    "!summary": "Get AI summary",
                    "!explain": "Get AI explanation"
                }
            }

            # Update embed with category commands
            category_key = next((k for k in commands.keys() if k in category), None)
            if category_key:
                embed.clear_fields()
                embed.title = f"📖 {category_key.title()} Commands"

                for cmd, desc in commands[category_key].items():
                    embed.add_field(
                        name=cmd,
                        value=f"```{desc}```",
                        inline=False
                    )

                await original_msg.edit(embed=embed)
                await self._show_tooltip(original_msg, f"✨ Showing {category_key.title()} commands!")

        except Exception as e:
            self.logger.error(f"Error showing category commands: {e}")

async def setup(bot):
    await bot.add_cog(InteractiveHelp(bot))