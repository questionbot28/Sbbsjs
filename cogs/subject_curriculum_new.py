import discord
from discord.ext import commands
import logging
from typing import Dict, Any, Tuple

class SubjectCurriculum(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger('discord_bot')
        self.subjects_data = {
            'accountancy': {
                11: [
                    "Introduction to Accounting",
                    "Theory Base of Accounting", 
                    "Recording of Transactions - I",
                    "Recording of Transactions - II",
                    "Bank Reconciliation Statement",
                    "Trial Balance and Rectification of Errors",
                    "Depreciation, Provisions and Reserves",
                    "Bills of Exchange",
                    "Financial Statements",
                    "Accounts from Incomplete Records",
                    "Applications of Computers in Accounting"
                ],
                12: [
                    "Accounting for Partnership Firms",
                    "Change in Profit Sharing Ratio",
                    "Admission of a Partner", 
                    "Retirement and Death of a Partner",
                    "Dissolution of Partnership",
                    "Accounting for Share Capital",
                    "Issue and Redemption of Debentures",
                    "Financial Statements of Companies",
                    "Analysis of Financial Statements",
                    "Cash Flow Statement",
                    "Computerized Accounting System"
                ]
            },
            'business_studies': {
                11: [
                    "Nature and Purpose of Business",
                    "Forms of Business Organisation",
                    "Private, Public and Global Enterprises",
                    "Business Services",
                    "Emerging Modes of Business",
                    "Social Responsibility of Business",
                    "Formation of a Company",
                    "Sources of Business Finance",
                    "Small Business",
                    "Internal Trade",
                    "International Business"
                ],
                12: [
                    "Nature and Significance of Management",
                    "Principles of Management",
                    "Business Environment",
                    "Planning",
                    "Organising",
                    "Staffing",
                    "Directing",
                    "Controlling",
                    "Financial Management",
                    "Financial Markets",
                    "Marketing Management",
                    "Consumer Protection"
                ]
            }
        }

    def _validate_subject(self, subject: str) -> Tuple[bool, str]:
        """Validate and normalize subject name"""
        subject_mapping = {
            'maths': 'mathematics',
            'math': 'mathematics',
            'bio': 'biology',
            'physics': 'physics',
            'chemistry': 'chemistry',
            'economics': 'economics',
            'accountancy': 'accountancy',
            'business': 'business_studies',
            'business_studies': 'business_studies',
            'english': 'english'
        }

        normalized_subject = subject.lower()
        normalized_subject = subject_mapping.get(normalized_subject, normalized_subject)

        if normalized_subject not in subject_mapping.values():
            return False, normalized_subject

        return True, normalized_subject

    @commands.command(name='chapters11')
    async def view_chapters_11(self, ctx, subject: str):
        """View chapters for class 11 subjects"""
        is_valid, normalized_subject = self._validate_subject(subject)
        if not is_valid:
            available_subjects = list(self.subjects_data.keys())
            formatted_subjects = [s.replace('_', ' ').title() for s in available_subjects]
            await ctx.send(f"❌ Invalid subject. Available subjects: {', '.join(formatted_subjects)}")
            return

        if normalized_subject not in self.subjects_data:
            await ctx.send("❌ Chapter data not available for this subject yet.")
            return

        chapters = self.subjects_data[normalized_subject][11]
        embed = discord.Embed(
            title=f"📚 {normalized_subject.replace('_', ' ').title()} - Class 11",
            description="Here are the chapters for your selected subject:",
            color=discord.Color.blue()
        )

        chapter_list = "\n".join([f"📖 {i+1}. {chapter}" for i, chapter in enumerate(chapters)])
        embed.add_field(
            name="Chapters",
            value=f"```{chapter_list}```",
            inline=False
        )

        embed.set_footer(text=f"Use !11 {normalized_subject.replace('_', ' ')} <chapter_name> to get questions!")
        await ctx.send(embed=embed)

    @commands.command(name='chapters12')
    async def view_chapters_12(self, ctx, subject: str):
        """View chapters for class 12 subjects"""
        is_valid, normalized_subject = self._validate_subject(subject)
        if not is_valid:
            available_subjects = list(self.subjects_data.keys())
            formatted_subjects = [s.replace('_', ' ').title() for s in available_subjects]
            await ctx.send(f"❌ Invalid subject. Available subjects: {', '.join(formatted_subjects)}")
            return

        if normalized_subject not in self.subjects_data:
            await ctx.send("❌ Chapter data not available for this subject yet.")
            return

        chapters = self.subjects_data[normalized_subject][12]
        embed = discord.Embed(
            title=f"📚 {normalized_subject.replace('_', ' ').title()} - Class 12",
            description="Here are the chapters for your selected subject:",
            color=discord.Color.blue()
        )

        chapter_list = "\n".join([f"📖 {i+1}. {chapter}" for i, chapter in enumerate(chapters)])
        embed.add_field(
            name="Chapters",
            value=f"```{chapter_list}```",
            inline=False
        )

        embed.set_footer(text=f"Use !12 {normalized_subject.replace('_', ' ')} <chapter_name> to get questions!")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(SubjectCurriculum(bot))
