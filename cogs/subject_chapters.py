import discord
from discord.ext import commands
from typing import Dict

class SubjectChapters(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.chapters = self._initialize_chapters()

    def _initialize_chapters(self) -> Dict[str, Dict[str, list]]:
        """Initialize the chapter lists for each subject"""
        return {
            'physics': {
                11: [
                    "Physical World and Measurement",
                    "Kinematics",
                    "Laws of Motion",
                    "Work, Energy and Power",
                    "Motion of System of Particles and Rigid Body",
                    "Gravitation",
                    "Properties of Bulk Matter",
                    "Thermodynamics",
                    "Behaviour of Perfect Gas and Kinetic Theory",
                    "Oscillations and Waves"
                ],
                12: [
                    "Electrostatics",
                    "Current Electricity",
                    "Magnetic Effects of Current and Magnetism",
                    "Electromagnetic Induction and Alternating Currents",
                    "Electromagnetic Waves",
                    "Optics",
                    "Dual Nature of Matter and Radiation",
                    "Atoms and Nuclei",
                    "Electronic Devices",
                    "Communication Systems"
                ]
            },
            'chemistry': {
                11: [
                    "Some Basic Concepts of Chemistry",
                    "Structure of Atom",
                    "Classification of Elements and Periodicity",
                    "Chemical Bonding and Molecular Structure",
                    "States of Matter",
                    "Thermodynamics",
                    "Equilibrium",
                    "Redox Reactions",
                    "Hydrogen",
                    "s-Block Elements",
                    "p-Block Elements",
                    "Organic Chemistry: Basic Principles"
                ],
                12: [
                    "Solutions",
                    "Electrochemistry",
                    "Chemical Kinetics",
                    "Surface Chemistry",
                    "General Principles of Isolation of Elements",
                    "p-Block Elements",
                    "d and f Block Elements",
                    "Coordination Compounds",
                    "Haloalkanes and Haloarenes",
                    "Alcohols, Phenols and Ethers",
                    "Aldehydes, Ketones and Carboxylic Acids",
                    "Amines",
                    "Biomolecules",
                    "Polymers",
                    "Chemistry in Everyday Life"
                ]
            },
            'mathematics': {
                11: [
                    "Sets",
                    "Relations and Functions",
                    "Trigonometric Functions",
                    "Principle of Mathematical Induction",
                    "Complex Numbers and Quadratic Equations",
                    "Linear Inequalities",
                    "Permutations and Combinations",
                    "Binomial Theorem",
                    "Sequences and Series",
                    "Straight Lines",
                    "Conic Sections",
                    "Introduction to Three Dimensional Geometry",
                    "Limits and Derivatives",
                    "Mathematical Reasoning",
                    "Statistics",
                    "Probability"
                ],
                12: [
                    "Relations and Functions",
                    "Inverse Trigonometric Functions",
                    "Matrices",
                    "Determinants",
                    "Continuity and Differentiability",
                    "Applications of Derivatives",
                    "Integrals",
                    "Applications of Integrals",
                    "Differential Equations",
                    "Vector Algebra",
                    "Three Dimensional Geometry",
                    "Linear Programming",
                    "Probability"
                ]
            },
            'biology': {
                11: [
                    "Diversity in Living World",
                    "Structural Organisation in Animals and Plants",
                    "Cell Structure and Function",
                    "Plant Physiology",
                    "Human Physiology"
                ],
                12: [
                    "Reproduction",
                    "Genetics and Evolution",
                    "Biology and Human Welfare",
                    "Biotechnology and Its Applications",
                    "Ecology and Environment"
                ]
            }
        }

    @commands.command(name='chapters')
    async def view_chapters(self, ctx, subject: str, class_level: int):
        """View chapters for a specific subject and class"""
        subject = subject.lower()
        if subject not in self.chapters:
            available_subjects = list(self.chapters.keys())
            await ctx.send(f"❌ Invalid subject. Available subjects: {', '.join(available_subjects)}")
            return

        if class_level not in [11, 12]:
            await ctx.send("❌ Please specify either class 11 or 12")
            return

        chapters = self.chapters[subject][class_level]
        
        embed = discord.Embed(
            title=f"📚 {subject.title()} Chapters - Class {class_level}",
            color=discord.Color.blue()
        )

        # Split chapters into groups of 10 for field limits
        chapter_groups = [chapters[i:i + 10] for i in range(0, len(chapters), 10)]
        
        for i, group in enumerate(chapter_groups, 1):
            chapter_text = "\n".join([f"📖 {i+1}. {chapter}" for i, chapter in enumerate(group)])
            embed.add_field(
                name=f"Chapters (Part {i})" if len(chapter_groups) > 1 else "Chapters",
                value=f"```{chapter_text}```",
                inline=False
            )

        embed.set_footer(text="Use these chapter names with !11 or !12 commands for topic-specific questions!")
        await ctx.send(embed=embed)

    @commands.command(name='allchapters')
    async def view_all_chapters(self, ctx):
        """View all chapters for all subjects"""
        for subject in self.chapters:
            for class_level in [11, 12]:
                chapters = self.chapters[subject][class_level]
                
                embed = discord.Embed(
                    title=f"📚 {subject.title()} - Class {class_level}",
                    color=discord.Color.blue()
                )

                # Split chapters into groups of 10 for field limits
                chapter_groups = [chapters[i:i + 10] for i in range(0, len(chapters), 10)]
                
                for i, group in enumerate(chapter_groups, 1):
                    chapter_text = "\n".join([f"📖 {i+1}. {chapter}" for i, chapter in enumerate(group)])
                    embed.add_field(
                        name=f"Chapters (Part {i})" if len(chapter_groups) > 1 else "Chapters",
                        value=f"```{chapter_text}```",
                        inline=False
                    )

                embed.set_footer(text=f"Use !{class_level} {subject} <chapter_name> to get questions!")
                await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(SubjectChapters(bot))
