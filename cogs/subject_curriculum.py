import discord
from discord.ext import commands
from typing import Dict, List

class SubjectCurriculum(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.subjects_data = {
            'mathematics': {
                11: [
                    "Sets",
                    "Relations and Functions",
                    "Trigonometric Functions",
                    "Complex Numbers",
                    "Linear Inequalities",
                    "Permutations and Combinations",
                    "Binomial Theorem",
                    "Sequences and Series",
                    "Straight Lines",
                    "Conic Sections",
                    "Introduction to 3D Geometry",
                    "Limits and Derivatives",
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
            'physics': {
                11: [
                    "Physical World",
                    "Units and Measurements",
                    "Motion in a Straight Line",
                    "Motion in a Plane",
                    "Laws of Motion",
                    "Work, Energy and Power",
                    "System of Particles and Rotational Motion",
                    "Gravitation",
                    "Mechanical Properties of Solids",
                    "Mechanical Properties of Fluids",
                    "Thermal Properties of Matter",
                    "Thermodynamics",
                    "Kinetic Theory",
                    "Oscillations",
                    "Waves"
                ],
                12: [
                    "Electric Charges and Fields",
                    "Electrostatic Potential and Capacitance",
                    "Current Electricity",
                    "Moving Charges and Magnetism",
                    "Magnetism and Matter",
                    "Electromagnetic Induction",
                    "Alternating Current",
                    "Electromagnetic Waves",
                    "Ray Optics and Optical Instruments",
                    "Wave Optics",
                    "Dual Nature of Radiation and Matter",
                    "Atoms",
                    "Nuclei",
                    "Semiconductor Electronics"
                ]
            },
            'chemistry': {
                11: [
                    "Some Basic Concepts of Chemistry",
                    "Structure of Atom",
                    "Classification of Elements",
                    "Chemical Bonding and Molecular Structure",
                    "States of Matter",
                    "Thermodynamics",
                    "Equilibrium",
                    "Redox Reactions",
                    "Hydrogen",
                    "s-Block Elements",
                    "p-Block Elements",
                    "Organic Chemistry",
                    "Hydrocarbons",
                    "Environmental Chemistry"
                ],
                12: [
                    "Solid State",
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
            'biology': {
                11: [
                    "Diversity in Living World",
                    "Structural Organisation in Plants and Animals",
                    "Cell Structure and Function",
                    "Plant Physiology",
                    "Human Physiology",
                    "Cell: The Unit of Life",
                    "Biomolecules",
                    "Cell Cycle and Cell Division",
                    "Transport in Plants",
                    "Mineral Nutrition",
                    "Photosynthesis in Higher Plants",
                    "Respiration in Plants",
                    "Plant Growth and Development",
                    "Digestion and Absorption",
                    "Breathing and Exchange of Gases",
                    "Body Fluids and Circulation",
                    "Excretory Products and their Elimination",
                    "Locomotion and Movement",
                    "Neural Control and Coordination",
                    "Chemical Coordination and Integration"
                ],
                12: [
                    "Reproduction in Organisms",
                    "Sexual Reproduction in Flowering Plants",
                    "Human Reproduction",
                    "Reproductive Health",
                    "Principles of Inheritance and Variation",
                    "Molecular Basis of Inheritance",
                    "Evolution",
                    "Human Health and Disease",
                    "Strategies for Enhancement in Food Production",
                    "Microbes in Human Welfare",
                    "Biotechnology: Principles and Processes",
                    "Biotechnology and its Applications",
                    "Organisms and Populations",
                    "Ecosystem",
                    "Biodiversity and Conservation",
                    "Environmental Issues"
                ]
            },
            'economics': {
                11: [
                    "Introduction to Economics",
                    "Collection of Data",
                    "Organisation of Data",
                    "Presentation of Data",
                    "Measures of Central Tendency",
                    "Measures of Dispersion",
                    "Correlation",
                    "Index Numbers",
                    "Consumer's Equilibrium and Demand",
                    "Producer Behaviour and Supply",
                    "Price Determination in a Perfect Market",
                    "Simple Applications of Tools of Demand and Supply"
                ],
                12: [
                    "National Income and Related Aggregates",
                    "Money and Banking",
                    "Determination of Income and Employment",
                    "Government Budget and the Economy",
                    "Balance of Payments",
                    "Development Experience (1947-90) and Economic Reforms since 1991",
                    "Current Challenges facing Indian Economy",
                    "Development Experience of India – A Comparison with Neighbours",
                    "Environment and Sustainable Development"
                ]
            },
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
                    "Accounting for Partnership Firms - Fundamentals",
                    "Change in Profit Sharing Ratio",
                    "Admission of a Partner",
                    "Retirement and Death of a Partner",
                    "Dissolution of Partnership Firm",
                    "Accounting for Share Capital",
                    "Issue and Redemption of Debentures",
                    "Financial Statements of Companies",
                    "Analysis of Financial Statements",
                    "Cash Flow Statement",
                    "Project Work"
                ]
            },
            'business_studies': {
                11: [
                    "Nature and Purpose of Business",
                    "Forms of Business Organisation",
                    "Public, Private and Global Enterprises",
                    "Business Services",
                    "Emerging Modes of Business",
                    "Social Responsibility of Business and Business Ethics",
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
            },
            'english': {
                11: [
                    "The Portrait of a Lady",
                    "We're Not Afraid to Die... if We Can All Be Together",
                    "Discovering Tut: the Saga Continues",
                    "Landscape of the Soul",
                    "The Ailing Planet: the Green Movement's Role",
                    "The Browning Version",
                    "The Adventure",
                    "Silk Road",
                    "Father to Son",
                    "Poetry",
                    "Writing Skills",
                    "Grammar"
                ],
                12: [
                    "The Last Lesson",
                    "Lost Spring",
                    "Deep Water",
                    "The Rattrap",
                    "Indigo",
                    "Poets and Pancakes",
                    "The Interview",
                    "Going Places",
                    "My Mother at Sixty-six",
                    "An Elementary School Classroom in a Slum",
                    "Keeping Quiet",
                    "A Thing of Beauty",
                    "A Roadside Stand",
                    "Aunt Jennifer's Tigers",
                    "Writing Skills",
                    "Advanced Grammar"
                ]
            }
        }

    @commands.command(name='chapters11')
    async def view_chapters_11(self, ctx, subject: str):
        """View chapters for class 11 subjects"""
        subject = subject.lower()
        if subject == 'business':
            subject = 'business_studies'

        if subject not in self.subjects_data:
            available_subjects = list(self.subjects_data.keys())
            formatted_subjects = [s.replace('_', ' ').title() for s in available_subjects]
            await ctx.send(f"❌ Invalid subject. Available subjects: {', '.join(formatted_subjects)}")
            return

        chapters = self.subjects_data[subject][11]
        embed = discord.Embed(
            title=f"📚 {subject.replace('_', ' ').title()} - Class 11",
            description="Here are the chapters for your selected subject:",
            color=discord.Color.blue()
        )

        chapter_list = "\n".join([f"📖 {i+1}. {chapter}" for i, chapter in enumerate(chapters)])
        embed.add_field(
            name="Chapters",
            value=f"```{chapter_list}```",
            inline=False
        )

        embed.set_footer(text=f"Use !11 {subject.replace('_', ' ')} <chapter_name> to get questions!")
        await ctx.send(embed=embed)

    @commands.command(name='chapters12')
    async def view_chapters_12(self, ctx, subject: str):
        """View chapters for class 12 subjects"""
        subject = subject.lower()
        if subject == 'business':
            subject = 'business_studies'

        if subject not in self.subjects_data:
            available_subjects = list(self.subjects_data.keys())
            formatted_subjects = [s.replace('_', ' ').title() for s in available_subjects]
            await ctx.send(f"❌ Invalid subject. Available subjects: {', '.join(formatted_subjects)}")
            return

        chapters = self.subjects_data[subject][12]
        embed = discord.Embed(
            title=f"📚 {subject.replace('_', ' ').title()} - Class 12",
            description="Here are the chapters for your selected subject:",
            color=discord.Color.blue()
        )

        chapter_list = "\n".join([f"📖 {i+1}. {chapter}" for i, chapter in enumerate(chapters)])
        embed.add_field(
            name="Chapters",
            value=f"```{chapter_list}```",
            inline=False
        )

        embed.set_footer(text=f"Use !12 {subject.replace('_', ' ')} <chapter_name> to get questions!")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(SubjectCurriculum(bot))
