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

    def _initialize_user_tracking(self, user_id: int, subject: str):
        """Initialize tracking for a user if not exists"""
        if user_id not in user_questions:
            user_questions[user_id] = {}
        if subject not in user_questions[user_id]:
            user_questions[user_id][subject] = {
                'used_questions': set(),
                'last_topic': None,
                'question_count': 0
            }

    async def _get_unique_question(self, user_id: int, subject: str, topic: Optional[str], class_level: int) -> Tuple[dict, bool]:
        """Get a unique question for the user, returns (question, is_new)"""
        self._initialize_user_tracking(user_id, subject)
        user_data = user_questions[user_id][subject]

        # Try to get a new question up to 3 times
        for _ in range(3):
            question = self.question_generator.get_stored_question(subject, topic, class_level)
            if question:
                question_key = f"{question['question'][:100]}"  # Use more of the question text as key
                if question_key not in user_data['used_questions']:
                    user_data['used_questions'].add(question_key)
                    user_data['last_topic'] = topic
                    user_data['question_count'] += 1
                    return question, True

        # If we couldn't get a new question, try generating a new one
        question = await self.question_generator.generate_question(subject, topic, class_level)
        if question:
            question_key = f"{question['question'][:100]}"
            if question_key not in user_data['used_questions']:
                user_data['used_questions'].add(question_key)
                user_data['question_count'] += 1
                return question, True

        return question, False

    @commands.command(name='11')
    async def class_11(self, ctx, subject: str, topic: Optional[str] = None):
        """Get a question for class 11"""
        if ctx.channel.id != 1337669136729243658:
            await ctx.send("❌ This command can only be used in the designated channel!")
            return

        try:
            subject = subject.lower()
            question, is_new = await self._get_unique_question(ctx.author.id, subject, topic, 11)

            if question:
                if not is_new:
                    await ctx.send("⚠️ Note: You've seen all available questions for this topic. Generating a new one...")
                await self._send_question(ctx, question)
            else:
                await ctx.send("❌ Sorry, I couldn't find a question for that subject/topic.")
        except Exception as e:
            self.logger.error(f"Error in class_11 command: {e}")
            await ctx.send("❌ An error occurred while getting your question.")

    @commands.command(name='12')
    async def class_12(self, ctx, subject: str, topic: Optional[str] = None):
        """Get a question for class 12"""
        if ctx.channel.id != 1337669207193682001:
            await ctx.send("❌ This command can only be used in the designated channel!")
            return

        try:
            subject = subject.lower()
            question, is_new = await self._get_unique_question(ctx.author.id, subject, topic, 12)

            if question:
                if not is_new:
                    await ctx.send("⚠️ Note: You've seen all available questions for this topic. Generating a new one...")
                await self._send_question(ctx, question)
            else:
                await ctx.send("❌ Sorry, I couldn't find a question for that subject/topic.")
        except Exception as e:
            self.logger.error(f"Error in class_12 command: {e}")
            await ctx.send("❌ An error occurred while getting your question.")

    async def _send_question(self, ctx, question: dict):
        """Format and send a question"""
        try:
            # Create question embed
            embed = discord.Embed(
                title="📝 Practice Question",
                description=question['question'],
                color=discord.Color.blue()
            )
            options_text = "\n".join(question['options'])
            embed.add_field(name="Options:", value=f"```{options_text}