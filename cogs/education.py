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
            "```\n"
            "Creator Information\n"
            "Made with love by: Rohanpreet Singh Pathania\n"
            "Language: Python\n"
            "```"
        )

        embed.add_field(
            name="👨‍💻 Credits",
            value=creator_info,
            inline=False
        )

        embed.set_footer(text="Use these commands to practice and learn! 📚✨")
        await ctx.send(embed=embed)

    @commands.command(name='11')
    async def class_11(self, ctx, subject: str, topic: Optional[str] = None):
        """Get a question for class 11"""
        if ctx.channel.id != 1337669136729243658:
            await ctx.send("❌ This command can only be used in the designated channel!")
            return

        try:
            subject = subject.lower()
            question = await self.question_generator.generate_question(subject, topic, 11)

            if question:
                question_key = f"{question['question'][:50]}"
                if self._is_question_asked(ctx.author.id, subject, question_key):
                    await ctx.send("🔄 Finding a new question you haven't seen before...")
                    question = await self.question_generator.generate_question(subject, topic, 11)

                if question:
                    self._mark_question_asked(ctx.author.id, subject, question_key)
                    await self._send_question(ctx, question)
                else:
                    await ctx.send("❌ Sorry, couldn't find a new question at this time.")
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
            question = await self.question_generator.generate_question(subject, topic, 12)

            if question:
                question_key = f"{question['question'][:50]}"
                if self._is_question_asked(ctx.author.id, subject, question_key):
                    await ctx.send("🔄 Finding a new question you haven't seen before...")
                    question = await self.question_generator.generate_question(subject, topic, 12)

                if question:
                    self._mark_question_asked(ctx.author.id, subject, question_key)
                    await self._send_question(ctx, question)
                else:
                    await ctx.send("❌ Sorry, couldn't find a new question at this time.")
            else:
                await ctx.send("❌ Sorry, I couldn't find a question for that subject/topic.")
        except Exception as e:
            self.logger.error(f"Error in class_12 command: {e}")
            await ctx.send("❌ An error occurred while getting your question.")

    def _is_question_asked(self, user_id: int, subject: str, question_key: str) -> bool:
        """Check if a question was already asked to a user"""
        return user_id in user_questions and \
               subject in user_questions.get(user_id, {}) and \
               question_key in user_questions[user_id][subject]

    def _mark_question_asked(self, user_id: int, subject: str, question_key: str):
        """Mark a question as asked for a user"""
        if user_id not in user_questions:
            user_questions[user_id] = {}
        if subject not in user_questions[user_id]:
            user_questions[user_id][subject] = set()
        user_questions[user_id][subject].add(question_key)

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
            embed.add_field(name="Options:", value=f"```{options_text}```", inline=False)

            # Send the question
            message = await ctx.send(embed=embed)

            # Add reaction options
            reactions = ['🇦', '🇧', '🇨', '🇩']
            for reaction in reactions:
                await message.add_reaction(reaction)

            # Send explanation in a separate embed
            explanation_embed = discord.Embed(
                title="📖 Explanation",
                description=f"```{question['explanation']}