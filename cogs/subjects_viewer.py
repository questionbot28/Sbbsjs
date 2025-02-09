
import discord
from discord.ext import commands
from typing import Dict

class SubjectsViewer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
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
            }
        }

    @commands.command(name='viewchapters11')
    async def view_chapters_11(self, ctx, subject: str):
        """View chapters for class 11 subjects"""
        subject = subject.lower()
        if subject not in self.subjects_data:
            available_subjects = list(self.subjects_data.keys())
            await ctx.send(f"❌ Invalid subject. Available subjects: {', '.join(available_subjects)}")
            return

        chapters = self.subjects_data[subject][11]
        embed = discord.Embed(
            title=f"📚 {subject.title()} - Class 11",
            color=discord.Color.blue()
        )

        chapter_text = "\n".join([f"📖 {i+1}. {chapter}" for i, chapter in enumerate(chapters)])
        embed.add_field(
            name="Chapters",
            value=f"```{chapter_text}```",
            inline=False
        )

        embed.set_footer(text=f"Use !11 {subject} <chapter_name> to get questions!")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(SubjectsViewer(bot))
