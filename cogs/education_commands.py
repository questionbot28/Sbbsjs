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

        creator_info = (
            "```ansi\n"
            "[0;35m┏━━━━━ Creator Information ━━━━━┓[0m\n"
            "[0;36m┃     Made with 💖 by:          ┃[0m\n"
            "[0;33m┃  Rohanpreet Singh Pathania   ┃[0m\n"
            "[0;36m┃     Language: Python 🐍      ┃[0m\n"
            "[0;35m┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛[0m\n"
            "```"
        )

        embed.add_field(
            name="👨‍💻 Credits",
            value=creator_info,
            inline=False
        )

        embed.set_footer(text="Use these commands to practice and learn! 📚✨")
        await ctx.send(embed=embed)

    def _initialize_user_tracking(self, user_id: int, subject: str) -> None:
        """Initialize tracking for a user if not exists"""
        if user_id not in self.user_questions:
            self.user_questions[user_id] = {}
        if subject not in self.user_questions[user_id]:
            self.user_questions[user_id][subject] = {
                'used_questions': set(),
                'last_topic': None,
                'question_count': 0
            }

    @commands.command(name='11')
    async def class_11(self, ctx, subject: str, topic: Optional[str] = None):
        """Get a question for class 11"""
        if ctx.channel.id != 1337669136729243658:
            await ctx.send("❌ This command can only be used in the designated channel!")
            return

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
                'business_studies': 'business_studies',
                'english': 'english'
            }

            subject = subject.lower()
            subject = subject_mapping.get(subject, subject)

            if subject not in subject_mapping.values():
                available_subjects = list(subject_mapping.keys())
                await ctx.send(f"❌ Invalid subject. Available subjects: {', '.join(available_subjects)}")
                return

            self._initialize_user_tracking(ctx.author.id, subject)
            question = await self.question_generator.generate_question(subject, topic, class_level=11)

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
                await ctx.send("❌ Sorry, I couldn't generate a question at this time. Please try again later.")

        except Exception as e:
            self.logger.error(f"Error in class_11 command: {str(e)}", exc_info=True)
            error_message = str(e)
            if "API key" in error_message:
                await ctx.send("❌ There's an issue with the API configuration. Please contact the bot administrator.")
            else:
                await ctx.send(f"❌ {error_message}")

    @commands.command(name='12')
    async def class_12(self, ctx, subject: str, topic: Optional[str] = None):
        """Get a question for class 12"""
        if ctx.channel.id != 1337669207193682001:
            await ctx.send("❌ This command can only be used in the designated channel!")
            return

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
                'business_studies': 'business_studies',
                'english': 'english'
            }

            subject = subject.lower()
            subject = subject_mapping.get(subject, subject)

            if subject not in subject_mapping.values():
                available_subjects = list(subject_mapping.keys())
                await ctx.send(f"❌ Invalid subject. Available subjects: {', '.join(available_subjects)}")
                return

            self._initialize_user_tracking(ctx.author.id, subject)
            question = await self.question_generator.generate_question(subject, topic, class_level=12)

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
                await ctx.send("❌ Sorry, I couldn't generate a question at this time. Please try again later.")

        except Exception as e:
            self.logger.error(f"Error in class_12 command: {str(e)}", exc_info=True)
            error_message = str(e)
            if "API key" in error_message:
                await ctx.send("❌ There's an issue with the API configuration. Please contact the bot administrator.")
            else:
                await ctx.send(f"❌ {error_message}")

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