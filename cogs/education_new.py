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

    async def get_question(self, subject: str, topic: Optional[str], class_level: int) -> Optional[dict]:
        """Get a question either from stored bank or generate one"""
        try:
            # Try to get stored question first
            if class_level == 11:
                question = get_stored_question_11(subject, topic)
            else:
                question = get_stored_question_12(subject, topic)

            if question:
                self.logger.info(f"Retrieved stored question for {subject} {topic if topic else ''}")
                return question

            # If no stored question, try to generate one
            self.logger.info(f"No stored question found, attempting to generate for {subject} {topic if topic else ''}")
            return await self.question_generator.generate_question(subject, topic, class_level)
        except Exception as e:
            self.logger.error(f"Error getting question: {str(e)}", exc_info=True)
            return None

    @commands.command(name='11')
    async def class_11(self, ctx, subject: str, topic: Optional[str] = None):
        """Get a question for class 11"""
        try:
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

            self.logger.info(f"Getting question for class 11, subject: {subject}, topic: {topic}")
            question = await self.get_question(subject, topic, 11)

            if question:
                embed = discord.Embed(
                    title="📝 Practice Question",
                    description=question['question'],
                    color=discord.Color.blue()
                )

                if 'options' in question:
                    options_text = "\n".join(question['options'])
                    embed.add_field(name="Options:", value=f"```{options_text}```", inline=False)

                await ctx.send(embed=embed)

                if 'correct_answer' in question:
                    answer_embed = discord.Embed(
                        title="✅ Answer",
                        description=f"Correct option: {question['correct_answer']}",
                        color=discord.Color.green()
                    )
                    if 'explanation' in question:
                        answer_embed.add_field(name="Explanation:", value=question['explanation'], inline=False)
                    await ctx.send(embed=answer_embed)
            else:
                available_subjects = list(subject_mapping.keys())
                await ctx.send(f"❌ Sorry, I couldn't find a question for that subject/topic.\nAvailable subjects: {', '.join(available_subjects)}")

        except Exception as e:
            self.logger.error(f"Error in class_11 command: {str(e)}", exc_info=True)
            await ctx.send("❌ An error occurred while getting your question.")

    @commands.command(name='12')
    async def class_12(self, ctx, subject: str, topic: Optional[str] = None):
        """Get a question for class 12"""
        try:
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

            question = await self.get_question(subject, topic, 12)
            if question:
                embed = discord.Embed(
                    title="📝 Practice Question",
                    description=question['question'],
                    color=discord.Color.blue()
                )

                if 'options' in question:
                    options_text = "\n".join(question['options'])
                    embed.add_field(name="Options:", value=f"```{options_text}```", inline=False)

                await ctx.send(embed=embed)

                if 'correct_answer' in question:
                    answer_embed = discord.Embed(
                        title="✅ Answer",
                        description=f"Correct option: {question['correct_answer']}",
                        color=discord.Color.green()
                    )
                    if 'explanation' in question:
                        answer_embed.add_field(name="Explanation:", value=question['explanation'], inline=False)
                    await ctx.send(answer_embed)
            else:
                available_subjects = list(subject_mapping.keys())
                await ctx.send(f"❌ Sorry, I couldn't find a question for that subject/topic.\nAvailable subjects: {', '.join(available_subjects)}")

        except Exception as e:
            self.logger.error(f"Error in class_12 command: {str(e)}", exc_info=True)
            await ctx.send("❌ An error occurred while getting your question.")

    @commands.command(name='subjects')
    async def list_subjects(self, ctx):
        """List all available subjects"""
        subjects = [
            'Mathematics',
            'Physics',
            'Chemistry',
            'Biology',
            'Economics',
            'Accountancy',
            'Business Studies',
            'English'
        ]

        embed = discord.Embed(
            title="📚 Available Subjects",
            description="Here are all the subjects you can study:",
            color=discord.Color.blue()
        )

        subject_list = "\n".join([f"• {subject}" for subject in subjects])
        embed.add_field(name="Subjects:", value=f"```{subject_list}