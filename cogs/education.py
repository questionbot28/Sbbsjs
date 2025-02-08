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

        embed.add_field(
            name="❓ Get Random Question",
            value="```!question```\nGet a random question from any subject",
            inline=False
        )

        creator_info = (
            "\n"
            "\u001b[35m┏━━━━━ Creator Information ━━━━━┓\u001b[0m\n"
            "\u001b[36m┃     Made with 💖 by:          ┃\u001b[0m\n"
            "\u001b[33m┃  Rohanpreet Singh Pathania   ┃\u001b[0m\n"
            "\u001b[36m┃     Language: Python 🐍      ┃\u001b[0m\n"
            "\u001b[35m┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\u001b[0m\n"
        )

        embed.add_field(
            name="👨‍💻 Credits",
            value=f"```ansi\n{creator_info}```",
            inline=False
        )

        embed.set_footer(text="Use these commands to practice and learn! 📚✨")
        await ctx.send(embed=embed)

    def _get_question_key(self, question: dict) -> str:
        """Generate a unique key for a question"""
        return f"{question['question'][:50]}"  # Use first 50 chars as key

    def _is_question_asked(self, user_id: int, subject: str, question_key: str) -> bool:
        """Check if a question was already asked to a user"""
        if user_id not in user_questions:
            user_questions[user_id] = {}
        if subject not in user_questions[user_id]:
            user_questions[user_id][subject] = set()
        return question_key in user_questions[user_id][subject]

    def _mark_question_asked(self, user_id: int, subject: str, question_key: str):
        """Mark a question as asked for a user"""
        user_questions[user_id][subject].add(question_key)

    async def _send_question(self, ctx, question: dict):
        """Format and send a question to the channel"""
        if not question:
            await ctx.send("❌ Sorry, I couldn't generate a question at this time.")
            return

        embed = discord.Embed(
            title="📝 Practice Question",
            description=question['question'],
            color=discord.Color.blue()
        )

        # Add options
        options_text = "\n".join(question['options'])
        embed.add_field(name="Options:", value=f"```{options_text}```", inline=False)

        # Add spoiler-tagged correct answer and explanation
        correct_answer = f"||{question['correct_answer']}||"
        embed.add_field(name="Correct Answer:", value=correct_answer, inline=True)

        explanation = f"||{question['explanation']}||"
        embed.add_field(name="Explanation:", value=explanation, inline=False)

        await ctx.send(embed=embed)

    @commands.command(name="11")
    async def class_11(self, ctx, subject: str, topic: Optional[str] = None):
        """Get a question for class 11"""
        try:
            subject = subject.lower()
            question = await self.question_generator.generate_question(subject, topic, 11)

            if question:
                question_key = self._get_question_key(question)
                if self._is_question_asked(ctx.author.id, subject, question_key):
                    await ctx.send("🔄 Finding a new question you haven't seen before...")
                    # Try to get another question
                    question = await self.question_generator.generate_question(subject, topic, 11)
                    if question:
                        question_key = self._get_question_key(question)
                        self._mark_question_asked(ctx.author.id, subject, question_key)
                        await self._send_question(ctx, question)
                    else:
                        await ctx.send("❌ Sorry, couldn't find a new question at this time.")
                else:
                    self._mark_question_asked(ctx.author.id, subject, question_key)
                    await self._send_question(ctx, question)
            else:
                await ctx.send("❌ Sorry, I couldn't find a question for that subject/topic.")
        except Exception as e:
            self.logger.error(f"Error in class_11 command: {e}")
            await ctx.send("❌ An error occurred while getting your question.")

    @commands.command(name="12")
    async def class_12(self, ctx, subject: str, topic: Optional[str] = None):
        """Get a question for class 12"""
        try:
            subject = subject.lower()
            question = await self.question_generator.generate_question(subject, topic, 12)

            if question:
                question_key = self._get_question_key(question)
                if self._is_question_asked(ctx.author.id, subject, question_key):
                    await ctx.send("🔄 Finding a new question you haven't seen before...")
                    # Try to get another question
                    question = await self.question_generator.generate_question(subject, topic, 12)
                    if question:
                        question_key = self._get_question_key(question)
                        self._mark_question_asked(ctx.author.id, subject, question_key)
                        await self._send_question(ctx, question)
                    else:
                        await ctx.send("❌ Sorry, couldn't find a new question at this time.")
                else:
                    self._mark_question_asked(ctx.author.id, subject, question_key)
                    await self._send_question(ctx, question)
            else:
                await ctx.send("❌ Sorry, I couldn't find a question for that subject/topic.")
        except Exception as e:
            self.logger.error(f"Error in class_12 command: {e}")
            await ctx.send("❌ An error occurred while getting your question.")

    @commands.command(name="subjects")
    async def list_subjects(self, ctx):
        """List all available subjects"""
        subjects = self.question_generator.get_subjects()

        embed = discord.Embed(
            title="📚 Available Subjects",
            description="Here are all the subjects you can study:",
            color=discord.Color.green()
        )

        subject_list = "\n".join([f"• {subject.title()}" for subject in subjects])
        embed.add_field(name="Subjects:", value=f"```{subject_list}```", inline=False)

        # Add creator info to subjects command too
        creator_info = (
            "\n"
            "\u001b[35m┏━━━━━ Creator Information ━━━━━┓\u001b[0m\n"
            "\u001b[36m┃     Made with 💖 by:          ┃\u001b[0m\n"
            "\u001b[33m┃  Rohanpreet Singh Pathania   ┃\u001b[0m\n"
            "\u001b[36m┃     Language: Python 🐍      ┃\u001b[0m\n"
            "\u001b[35m┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\u001b[0m\n"
        )

        embed.add_field(
            name="👨‍💻 Credits",
            value=f"```ansi\n{creator_info}