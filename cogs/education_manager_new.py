\n"
            "!11 - Get Class 11 Questions\n"
            "!12 - Get Class 12 Questions\n"
            "!subjects - List All Subjects\n"
            "!chapters11 - View Class 11 Chapters\n"
            "!chapters12 - View Class 12 Chapters\n"
            "```"
        )
        help_embed.add_field(
            name="🎮 Available Commands",
            value=commands_info,
            inline=False
        )

        examples = (
            "```\n"
            "!11 physics waves\n"
            "!12 chemistry organic\n"
            "!chapters11 physics\n"
            "!chapters12 chemistry\n"
            "```"
        )
        help_embed.add_field(
            name="📝 Example Usage",
            value=examples,
            inline=False
        )

        features = (
            "• 📚 Questions from all major subjects\n"
            "• 🎯 Topic-specific practice\n"
            "• 📖 Chapter-wise curriculum view\n"
            "• ⏱️ Timed answer reveals\n"
            "• 📨 Private message delivery\n"
            "• 📝 Detailed explanations"
        )
        help_embed.add_field(
            name="✨ Features",
            value=features,
            inline=False
        )

        help_embed.set_footer(text="Made with ❤️ by Rohanpreet Singh Pathania")
        await ctx.send(embed=help_embed)

    @commands.command(name='subjects')
    async def list_subjects(self, ctx):
        """List all available subjects"""
        embed = discord.Embed(
            title="📚 Available Subjects",
            description="Here are all the subjects you can study:",
            color=discord.Color.blue()
        )

        subjects_format = (
            "📕 Mathematics\n"
            "📗 Physics\n"
            "📘 Chemistry\n"
            "📙 Biology\n"
            "📔 Economics\n"
            "📓 Accountancy\n"
            "📒 Business Studies\n"
            "📚 English"
        )
        embed.add_field(
            name="Available Subjects:",
            value=f"```{subjects_format}```",
            inline=False
        )

        examples = (
            "Examples:\n"
            "!11 physics waves\n"
            "!12 chemistry organic\n"
            "!11 mathematics integration\n"
            "!12 biology evolution"
        )
        embed.add_field(
            name="How to Use:",
            value=f"```{examples}```",
            inline=False
        )

        embed.set_footer(text="Use these subjects with !11 or !12 commands to get practice questions! 📚✨")
        await ctx.send(embed=embed)

    @commands.command(name='11')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def class_11(self, ctx, subject: str, topic: Optional[str] = None):
        """Get a question for class 11"""
        await self._handle_question_command(ctx, subject, topic, 11)

    @commands.command(name='12')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def class_12(self, ctx, subject: str, topic: Optional[str] = None):
        """Get a question for class 12"""
        await self._handle_question_command(ctx, subject, topic, 12)

    async def _handle_question_command(self, ctx, subject: str, topic: Optional[str], class_level: int):
        """Handle question generation for both class 11 and 12"""
        if ctx.author.id not in self.command_locks:
            self.command_locks[ctx.author.id] = asyncio.Lock()

        async with self.command_locks[ctx.author.id]:
            try:
                # Validate subject
                is_valid, normalized_subject = self._validate_subject(subject)
                if not is_valid:
                    available_subjects = ['Mathematics', 'Physics', 'Chemistry', 'Biology',
                                          'Economics', 'Accountancy', 'Business Studies', 'English']
                    await ctx.send(f"❌ Invalid subject. Available subjects: {', '.join(available_subjects)}")
                    return

                # Initialize tracking for this user and subject
                if ctx.author.id not in self.user_questions:
                    self.user_questions[ctx.author.id] = {}

                # Generate question
                try:
                    question = await self.question_generator.generate_question(
                        subject=normalized_subject,
                        topic=topic,
                        class_level=class_level,
                        user_id=str(ctx.author.id)
                    )

                    if not question:
                        await ctx.send("❌ Unable to generate a question at this time. Please try again.")
                        return

                    # Send question to DM
                    await self.send_question_to_dm(ctx, question)

                except Exception as e:
                    self.logger.error(f"Error generating question: {str(e)}")
                    error_message = str(e)
                    if "API key" in error_message:
                        await ctx.send("❌ There's an issue with the API configuration. Please contact the bot administrator.")
                    else:
                        await ctx.send(f"❌ An error occurred while getting your question: {error_message}")

            except Exception as e:
                self.logger.error(f"Error in question command: {str(e)}")
                await ctx.send("❌ An error occurred while processing your request.")

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

    async def send_question_to_dm(self, ctx, question_data: Dict[str, Any]):
        """Send a question to user's DM with fancy formatting"""
        try:
            question_embed = discord.Embed(
                title="📝 Practice Question",
                description=question_data['question'],
                color=discord.Color.blue()
            )

            if 'options' in question_data:
                options_text = "\n".join(question_data['options'])
                question_embed.add_field(
                    name="Options:",
                    value=f"```{options_text}