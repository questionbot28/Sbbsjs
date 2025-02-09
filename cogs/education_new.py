!11 <subject> [topic]```\nExample: !11 physics waves",
            inline=False
        )

        embed.add_field(
            name="📗 Get Question for Class 12", 
            value="```!12 <subject> [topic]```\nExample: !12 chemistry organic",
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
            question = await self._get_unique_question(ctx, subject, topic, 11)
            if question:
                embed = discord.Embed(
                    title="📝 Practice Question",
                    description=question['question'],
                    color=discord.Color.blue()
                )
                if 'options' in question:
                    options_text = "\n".join(question['options'])
                    embed.add_field(name="Options:", value=options_text, inline=False)
                await ctx.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Error in class_11 command: {e}")
            await ctx.send("❌ An error occurred while getting your question.")

    @commands.command(name='12')
    async def class_12(self, ctx, subject: str, topic: Optional[str] = None):
        """Get a question for class 12"""
        try:
            question = await self._get_unique_question(ctx, subject, topic, 12)
            if question:
                embed = discord.Embed(
                    title="📝 Practice Question",
                    description=question['question'],
                    color=discord.Color.blue()
                )
                if 'options' in question:
                    options_text = "\n".join(question['options'])
                    embed.add_field(name="Options:", value=options_text, inline=False)
                await ctx.send(embed=embed)
            else:
                await ctx.send("❌ Sorry, I couldn't find a question for that subject/topic.")

        except Exception as e:
            self.logger.error(f"Error in class_12 command: {e}")
            await ctx.send("❌ An error occurred while getting your question.")


    async def _get_unique_question(self, ctx, subject: str, topic: Optional[str], class_level: int):
        """Get a question for the given subject and topic"""
        try:
            import random
            from question_bank_11 import QUESTION_BANK_11 # Assumed import
            subject = subject.lower()

            # Get all available questions for the subject/topic
            if subject in QUESTION_BANK_11:
                if isinstance(QUESTION_BANK_11[subject], dict):
                    if topic:
                        questions = QUESTION_BANK_11[subject].get(topic, [])
                    else:
                        questions = []
                        for topic_questions in QUESTION_BANK_11[subject].values():
                            questions.extend(topic_questions)
                else:
                    questions = QUESTION_BANK_11[subject]

                if questions:
                    return random.choice(questions)

            return None # Return None if no question is found

        except Exception as e:
            self.logger.error(f"Error in _get_unique_question: {e}")
            return None

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