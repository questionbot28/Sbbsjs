
import discord
from discord.ext import commands
from typing import Dict

class SubjectsViewer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.subjects_data = {
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

    @commands.command(name='class')
    async def view_class_subject_chapters(self, ctx, subject: str = None):
        """View chapters for a subject in both classes"""
        if not subject:
            await ctx.send("❌ Please specify a subject. Example: !class physics")
            return
            
        subject = subject.lower()
        if subject not in self.subjects_data:
            available_subjects = list(self.subjects_data.keys())
            await ctx.send(f"❌ Invalid subject. Available subjects: {', '.join(available_subjects)}")
            return

        for class_level in [11, 12]:
            chapters = self.subjects_data[subject][class_level]
            
            embed = discord.Embed(
                title=f"📚 {subject.title()} - Class {class_level}",
                color=discord.Color.blue()
            )

            # Split chapters into groups of 10 for field limits
            chapter_groups = [chapters[i:i + 10] for i in range(0, len(chapters), 10)]
            
            for i, group in enumerate(chapter_groups, 1):
                chapter_text = "\n".join([f"📖 {j+1}. {chapter}" for j, chapter in enumerate(group)])
                embed.add_field(
                    name=f"Chapters (Part {i})" if len(chapter_groups) > 1 else "Chapters",
                    value=f"```{chapter_text}```",
                    inline=False
                )

            embed.set_footer(text=f"Use !{class_level} {subject} <chapter_name> to get questions!")
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(SubjectsViewer(bot))
