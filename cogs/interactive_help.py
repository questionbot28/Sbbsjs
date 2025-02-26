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
            "learning": ("🎓", discord.ButtonStyle.success),
            "music": ("🎵", discord.ButtonStyle.primary),
            "invites": ("📊", discord.ButtonStyle.success),
            "ai": ("🤖", discord.ButtonStyle.primary)
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
            "⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"
        ]

    @commands.command(name='help2', description='Shows the new interactive help menu')
    async def interactive_help(self, ctx):
        """Display the interactive help menu with animated tooltips"""
        try:
            embed = discord.Embed(
                title="🌟 EduSphere Interactive Command Center 🌟",
                description=(
                    "🔹 Welcome to the ultimate control hub!\n"
                    "🔹 Select a category to access its commands.\n\n"
                    "⬇️ Click a category to reveal specific features! ⬇️\n\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    "📂 **MAIN CATEGORIES** 📂\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                ),
                color=discord.Color.blue()
            )

            categories = {
                "🎵 MUSIC SYSTEM": "Play, pause, loop & apply effects to music",
                "📚 EDUCATION HUB": "Generate papers, quizzes & AI study notes",
                "🎓 LEARNING ASSISTANT": "Access learning assistant and tips features",
                "📊 INVITE TRACKER": "Track invites & climb the leaderboard",
                "🤖 AI ASSISTANT": "Chat with AI & get instant help"
            }

            category_text = "\n".join([f"🔹 **{cat}** – {desc}" for cat, desc in categories.items()])
            embed.description += category_text

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
            self.logger.info(f"Category selected: {category} by user {interaction.user.name}")
            commands = {
                "education": {
                    "!11": "Generate Class 11 practice questions",
                    "!12": "Generate Class 12 practice questions",
                    "!subjects": "View all available subjects",
                    "!chapters11": "Browse Class 11 chapters",
                    "!chapters12": "Browse Class 12 chapters"
                },
                "learning": {
                    "!learn": "Access learning assistant features",
                    "!learn quiz": "Get personalized practice questions",
                    "!learn schedule": "Create custom study schedules",
                    "!learn solve": "Get step-by-step solutions",
                    "!tips": "Manage your study tips",
                    "!tips category": "Create/manage tip categories",
                    "!tips add": "Add new study tips",
                    "!tips view": "View tips by category"
                },
                "music": {
                    "!play": "Play your favorite songs & playlists",
                    "!pause": "Pause the current track",
                    "!resume": "Resume paused music",
                    "!skip": "Skip to the next song",
                    "!queue": "View upcoming tracks",
                    "!volume": "Adjust music volume",
                    "!lyrics": "Show song lyrics",
                    "!now": "Display current track"
                },
                "invites": {
                    "!invites": "Check your invite statistics",
                    "!invite-stats": "View detailed analytics",
                    "!invite-history": "Track invite progress",
                    "!invite-leaderboard": "Compete with others"
                },
                "ai": {
                    "!ask": "Get instant AI answers",
                    "!chat": "Start AI conversation",
                    "!summary": "Summarize text with AI",
                    "!explain": "Get detailed explanations",
                    "!study": "Generate study materials",
                    "!quiz": "Create AI-powered quizzes"
                }
            }

            embed = discord.Embed(
                title=f"🌟 {category.upper()} COMMANDS 🌟",
                description=(
                    f"🔹 Welcome to {category.title()} Commands!\n"
                    f"🔹 Here are all the available features:\n\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                ),
                color=discord.Color.blue()
            )

            command_text = "\n\n".join([f"**{cmd}**\n➜ {desc}" for cmd, desc in commands[category].items()])
            embed.description += f"\n{command_text}"

            embed.set_footer(text=f"✨ Browsing {category.title()} commands • Click another category to explore more!")
            view = HelpMenuView(self)
            await interaction.response.edit_message(embed=embed, view=view)

            if interaction.message.id in self.active_menus.values():
                await self._show_tooltip(interaction.message, f"✨ Showing {category.title()} commands!")
                self.logger.info(f"Successfully displayed {category} commands for user {interaction.user.name}")

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