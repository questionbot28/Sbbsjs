import discord
from discord.ext import commands
import logging
import asyncio
from typing import Dict, Any, Optional, Tuple

class EducationManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger('discord_bot')
        self.command_locks = {}
        self.user_questions = {}
        self.subjects_data = {
            'physics': {
                11: ['Motion', 'Laws of Motion', 'Work, Energy and Power', 'Rotational Motion',
                     'Gravitation', 'Properties of Solids and Liquids', 'Thermodynamics',
                     'Kinetic Theory of Gases', 'Oscillations', 'Waves'],
                12: ['Electric Charges and Fields', 'Electrostatic Potential', 'Current Electricity',
                     'Moving Charges and Magnetism', 'Magnetism and Matter', 'Electromagnetic Induction',
                     'Alternating Current', 'Electromagnetic Waves', 'Ray Optics', 'Wave Optics',
                     'Dual Nature of Matter and Radiation', 'Atoms', 'Nuclei', 'Semiconductor Electronics']
            },
            'chemistry': {
                11: ['Some Basic Concepts', 'Structure of Atom', 'Classification of Elements',
                     'Chemical Bonding', 'States of Matter', 'Thermodynamics', 'Equilibrium',
                     'Redox Reactions', 'Hydrogen', 's-Block Elements', 'Organic Chemistry'],
                12: ['Solid State', 'Solutions', 'Electrochemistry', 'Chemical Kinetics',
                     'Surface Chemistry', 'General Principles of Isolation', 'p-Block Elements',
                     'd and f Block Elements', 'Coordination Compounds', 'Haloalkanes and Haloarenes',
                     'Alcohols, Phenols and Ethers', 'Aldehydes, Ketones and Carboxylic Acids',
                     'Amines', 'Biomolecules', 'Polymers', 'Chemistry in Everyday Life']
            }
        }
        self.dm_gif_url = "https://media.tenor.com/ZzYVQu_3iYEAAAAi/dm-message.gif"
        self.option_emojis = {
            'A': '🅰️',
            'B': '🅱️',
            'C': '©️',
            'D': '📝'
        }

    @commands.command(name='refresh')
    @commands.has_permissions(administrator=True)
    async def refresh(self, ctx):
        """Refresh bot by reloading all extensions"""
        loading_msg = await ctx.send("🔄 Reloading all extensions...")

        try:
            # Unload all extensions first
            for extension in list(self.bot.extensions):
                await self.bot.unload_extension(extension)

            # Load all extensions
            extensions = [
                'cogs.education_manager',
                'cogs.subject_curriculum_new',
                'cogs.admin'
            ]

            for extension in extensions:
                await self.bot.load_extension(extension)
                self.logger.info(f"Successfully reloaded extension: {extension}")

            await loading_msg.edit(content="✨ All extensions and commands have been reloaded successfully! ✨")

        except Exception as e:
            self.logger.error(f"Error refreshing bot: {e}")
            await loading_msg.edit(content=f"❌ Error refreshing bot: {str(e)}")
            # Try to load back the extensions that were unloaded
            try:
                for extension in extensions:
                    if extension not in self.bot.extensions:
                        await self.bot.load_extension(extension)
            except Exception as reload_error:
                self.logger.error(f"Error reloading extensions after failure: {reload_error}")

    @commands.command(name='chapters11')
    async def view_chapters_11(self, ctx, subject: str):
        """View chapters for class 11 subjects"""
        subject = subject.lower()
        if subject not in self.subjects_data:
            available_subjects = list(self.subjects_data.keys())
            formatted_subjects = [s.replace('_', ' ').title() for s in available_subjects]
            await ctx.send(f"❌ Invalid subject. Available subjects: {', '.join(formatted_subjects)}")
            return

        chapters = self.subjects_data[subject][11]
        embed = discord.Embed(
            title=f"📚 {subject.title()} - Class 11",
            description="Here are the chapters for your selected subject:",
            color=discord.Color.blue()
        )

        chapter_list = "\n".join([f"📖 {i+1}. {chapter}" for i, chapter in enumerate(chapters)])
        embed.add_field(
            name="Chapters",
            value=f"```{chapter_list}```",
            inline=False
        )

        embed.set_footer(text=f"Use !11 {subject} <chapter_name> to get questions!")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(EducationManager(bot))
