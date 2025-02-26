import discord
from discord.ext import commands
from discord.ui import View, Button
import logging
from typing import Dict, Optional

class CommandExplainView(View):
    def __init__(self, cog, command_name: str, timeout=60):
        super().__init__(timeout=timeout)
        self.cog = cog
        self.command_name = command_name
        self.add_explanation_buttons()

    def add_explanation_buttons(self):
        buttons = [
            ("🔍 How it Works", discord.ButtonStyle.primary, "how"),
            ("📝 Examples", discord.ButtonStyle.success, "examples"),
            ("💡 Tips & Tricks", discord.ButtonStyle.secondary, "tips")
        ]

        for label, style, custom_id in buttons:
            button = Button(
                style=style,
                label=label,
                custom_id=f"cmdhelp_{self.command_name}_{custom_id}"
            )
            button.callback = lambda i, type=custom_id: self.cog.handle_explain_button(i, self.command_name, type)
            self.add_item(button)

class CommandExplainer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger('discord_bot')
        self.command_info = {
            # Education Commands
            "11": {
                "category": "Education",
                "description": "Generate Class 11 practice questions",
                "syntax": "!11 <subject> [topic]",
                "examples": ["!11 physics waves", "!11 chemistry organic"],
                "tips": ["Specify topics for targeted practice", "Questions are sent via DM for privacy"]
            },
            "12": {
                "category": "Education",
                "description": "Generate Class 12 practice questions",
                "syntax": "!12 <subject> [topic]",
                "examples": ["!12 physics mechanics", "!12 maths calculus"],
                "tips": ["Be specific with topics for better questions", "Check DMs for questions"]
            },
            "subjects": {
                "category": "Education",
                "description": "View all available subjects",
                "syntax": "!subjects",
                "examples": ["!subjects"],
                "tips": ["Use these subjects with !11 or !12", "All subjects regularly updated"]
            },
            "chapters11": {
                "category": "Education",
                "description": "View chapters for Class 11 subjects",
                "syntax": "!chapters11 <subject>",
                "examples": ["!chapters11 physics", "!chapters11 maths"],
                "tips": ["See complete chapter list", "Use chapter names with !11 command"]
            },
            "chapters12": {
                "category": "Education",
                "description": "View chapters for Class 12 subjects",
                "syntax": "!chapters12 <subject>",
                "examples": ["!chapters12 chemistry", "!chapters12 accountancy"],
                "tips": ["See complete chapter list", "Use chapter names with !12 command"]
            },
            # Music Commands
            "play": {
                "category": "Music",
                "description": "Play music from various sources",
                "syntax": "!play <song name or URL>",
                "examples": ["!play Believer", "!play https://youtube.com/..."],
                "tips": ["Works with YouTube URLs", "Supports playlist links", "Queue multiple songs"]
            },
            "queue": {
                "category": "Music",
                "description": "View music queue",
                "syntax": "!queue",
                "examples": ["!queue"],
                "tips": ["Shows upcoming tracks", "Displays current track progress"]
            },
            "volume": {
                "category": "Music",
                "description": "Adjust music volume",
                "syntax": "!volume <0-100>",
                "examples": ["!volume 50", "!volume 75"],
                "tips": ["0 for mute", "100 for max volume"]
            },
            "lyrics": {
                "category": "Music",
                "description": "Show song lyrics",
                "syntax": "!lyrics [song name]",
                "examples": ["!lyrics", "!lyrics Shape of You"],
                "tips": ["Without song name shows current song", "Supports most languages"]
            },
            # AI Commands
            "ask": {
                "category": "AI",
                "description": "Get AI-powered answers",
                "syntax": "!ask <your question>",
                "examples": ["!ask explain quantum physics", "!ask solve quadratic equations"],
                "tips": ["Be specific in questions", "Use clear language"]
            },
            "chat": {
                "category": "AI",
                "description": "Start AI conversation",
                "syntax": "!chat <message>",
                "examples": ["!chat Hello AI!", "!chat Help me study"],
                "tips": ["Natural conversation", "Context-aware responses"]
            },
            "study": {
                "category": "AI",
                "description": "Generate study materials",
                "syntax": "!study <topic>",
                "examples": ["!study photosynthesis", "!study calculus"],
                "tips": ["Generates notes & examples", "Subject-specific help"]
            },
            # Invite System
            "invites": {
                "category": "Invites",
                "description": "Check invite statistics",
                "syntax": "!invites",
                "examples": ["!invites"],
                "tips": ["Shows total invites", "Track server growth"]
            },
            "invite-leaderboard": {
                "category": "Invites",
                "description": "View top inviters",
                "syntax": "!invite-leaderboard",
                "examples": ["!invite-leaderboard"],
                "tips": ["Real-time updates", "Shows top 10"]
            },
            # Help Commands
            "help2": {
                "category": "Help",
                "description": "Interactive help menu",
                "syntax": "!help2",
                "examples": ["!help2"],
                "tips": ["Click buttons to explore", "Category-based navigation"]
            },
            "cmdhelp": {
                "category": "Help",
                "description": "Get command explanations",
                "syntax": "!cmdhelp [command]",
                "examples": ["!cmdhelp", "!cmdhelp play"],
                "tips": ["Shows all commands if no name given", "Detailed command guides"]
            }
        }
        self.logger.info("CommandExplainer cog initialized successfully")

    @commands.command(name="cmdhelp")
    async def command_help(self, ctx, command_name: Optional[str] = None):
        """Get a detailed explanation of how a command works"""
        try:
            self.logger.info(f"Command help requested by {ctx.author} for command: {command_name}")

            if not command_name:
                self.logger.debug("No specific command requested, showing available commands")
                await self.show_available_commands(ctx)
                return

            command_name = command_name.lower().strip('!')
            if command_name not in self.command_info:
                self.logger.warning(f"Invalid command requested: {command_name}")
                await ctx.send(f"❌ Command `{command_name}` not found. Use `!cmdhelp` to see available commands.")
                return

            self.logger.debug(f"Generating help embed for command: {command_name}")
            embed = discord.Embed(
                title=f"📚 Command Guide: !{command_name}",
                description=(
                    f"**Category:** {self.command_info[command_name]['category']}\n"
                    f"**Description:** {self.command_info[command_name]['description']}\n"
                    f"**Usage:** `{self.command_info[command_name]['syntax']}`\n\n"
                    "Click the buttons below for more details!"
                ),
                color=discord.Color.blue()
            )

            view = CommandExplainView(self, command_name)
            await ctx.send(embed=embed, view=view)
            self.logger.info(f"Successfully sent command help for {command_name}")

        except Exception as e:
            self.logger.error(f"Error in command help: {str(e)}", exc_info=True)
            await ctx.send("❌ An error occurred while explaining the command.")

    async def handle_explain_button(self, interaction: discord.Interaction, command_name: str, explain_type: str):
        """Handle explanation button clicks"""
        try:
            self.logger.info(f"Button clicked: {explain_type} for command {command_name} by {interaction.user}")
            embed = discord.Embed(
                title=f"📚 !{command_name} - {explain_type.title()}",
                color=discord.Color.blue()
            )

            if explain_type == "how":
                embed.description = (
                    f"**How it Works:**\n"
                    f"1. Command: `{self.command_info[command_name]['syntax']}`\n"
                    f"2. Category: {self.command_info[command_name]['category']}\n"
                    f"3. Purpose: {self.command_info[command_name]['description']}\n"
                )

            elif explain_type == "examples":
                examples = "\n".join([f"• `{ex}`" for ex in self.command_info[command_name]['examples']])
                embed.description = f"**Example Usage:**\n{examples}"

            elif explain_type == "tips":
                tips = "\n".join([f"💡 {tip}" for tip in self.command_info[command_name]['tips']])
                embed.description = f"**Tips & Tricks:**\n{tips}"

            view = CommandExplainView(self, command_name)
            await interaction.response.edit_message(embed=embed, view=view)
            self.logger.info(f"Successfully updated explanation for {command_name}")

        except Exception as e:
            self.logger.error(f"Error handling explain button: {str(e)}", exc_info=True)
            await interaction.response.send_message(
                "❌ An error occurred while showing the explanation.",
                ephemeral=True
            )

    async def show_available_commands(self, ctx):
        """Show list of commands that can be explained"""
        try:
            self.logger.debug("Generating available commands list")
            embed = discord.Embed(
                title="🔍 Available Commands Guide",
                description="Here are the commands you can get explanations for:",
                color=discord.Color.blue()
            )

            categories = {}
            for cmd, info in self.command_info.items():
                cat = info['category']
                if cat not in categories:
                    categories[cat] = []
                categories[cat].append(f"`!{cmd}`")

            for category, commands in categories.items():
                embed.add_field(
                    name=f"{category} Commands",
                    value=" • ".join(commands),
                    inline=False
                )

            embed.set_footer(text="Use !cmdhelp <command> to get detailed explanations!")
            await ctx.send(embed=embed)
            self.logger.info("Successfully displayed available commands")

        except Exception as e:
            self.logger.error(f"Error showing available commands: {str(e)}", exc_info=True)
            await ctx.send("❌ An error occurred while listing commands.")

async def setup(bot):
    await bot.add_cog(CommandExplainer(bot))
    logging.getLogger('discord_bot').info("CommandExplainer cog loaded successfully")