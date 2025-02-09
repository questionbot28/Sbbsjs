!11 <subject> [topic]```\nExample: !11 physics waves",
            inline=False
        )

        embed.add_field(
            name="📗 Get Question for Class 12", 
            value="```!12 <subject> [topic]```\nExample: !12 chemistry electrochemistry",
            inline=False
        )

        embed.add_field(
            name="📋 List Available Subjects",
            value="```!subjects```\nShows all subjects you can study",
            inline=False
        )

        embed.set_footer(text="Use these commands to practice and learn! 📚✨")
        await ctx.send(embed=embed)

    @commands.command(name='11')
    async def class_11(self, ctx, subject: str, topic: Optional[str] = None):
        """Get a question for class 11"""
        try:
            # Map common subject names to standardized versions
            subject_mapping = {
                'maths': 'mathematics',
                'math': 'mathematics',
                'bio': 'biology',
                'physics': 'physics',
                'chemistry': 'chemistry',
                'economics': 'economics',
                'accountancy': 'accountancy',
                'business': 'business_studies',
                'business_studies': 'business_studies'
            }

            subject = subject.lower()
            subject = subject_mapping.get(subject, subject)

            from question_bank_11 import get_stored_question_11
            stored_question = get_stored_question_11(subject, topic)
            if stored_question:
                await ctx.send(embed=discord.Embed(
                    title="📝 Practice Question",
                    description=stored_question['question'],
                    color=discord.Color.blue()
                ).add_field(
                    name="Options:",
                    value="\n".join(stored_question['options']),
                    inline=False
                ))
            else:
                await ctx.send("❌ Sorry, I couldn't find a question for that subject/topic.")
        except Exception as e:
            await ctx.send("❌ An error occurred while getting your question.")

    @commands.command(name='12')
    async def class_12(self, ctx, subject: str, topic: Optional[str] = None):
        """Get a question for class 12"""
        await ctx.send(f"Getting a question for class 12 {subject} {topic if topic else ''}")

    @commands.command(name='subjects')
    async def list_subjects(self, ctx):
        """List all available subjects"""
        subjects = [
            'Mathematics', 'Physics', 'Chemistry', 'Biology',
            'Economics', 'Accountancy', 'Business Studies'
        ]

        embed = discord.Embed(
            title="📚 Available Subjects",
            description="Here are all the subjects you can study:",
            color=discord.Color.blue()
        )

        subject_list = "\n".join([f"• {subject}" for subject in subjects])
        embed.add_field(name="Subjects:", value=f"```{subject_list}