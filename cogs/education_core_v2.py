\n"
            "[1;34m┏━━━━━ Class 11 & 12 Subjects ━━━━━┓[0m\n"
            "📕 Mathematics\n"
            "📗 Physics\n"
            "📘 Chemistry\n"
            "📙 Biology\n"
            "📔 Economics\n"
            "📓 Accountancy\n"
            "📒 Business Studies\n"
            "📚 English\n"
            "[1;34m┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛[0m\n"
            "```"
        )
        embed.add_field(name="Available Subjects:", value=subjects_format, inline=False)

        examples = (
            "```\n"
            "Examples:\n"
            "!11 physics waves\n"
            "!12 chemistry organic\n"
            "!11 mathematics integration\n"
            "!12 biology evolution\n"
            "```"
        )
        embed.add_field(name="How to Use:", value=examples, inline=False)
        embed.set_footer(text="Use these subjects with !11 or !12 commands to get practice questions! 📚✨")
        await ctx.send(embed=embed)

    @commands.command(name='refresh')
    @commands.has_permissions(administrator=True)
    async def refresh(self, ctx):
        """Refresh the bot (Admin only)"""
        try:
            await ctx.send("🔄 Refreshing bot...")
            # Reload all cogs
            for extension in list(self.bot.extensions):
                await self.bot.reload_extension(extension)
            await ctx.send("✅ Bot refreshed successfully!")
        except Exception as e:
            await ctx.send(f"❌ Error refreshing bot: {str(e)}")

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
                    value=f"```{options_text}```",
                    inline=False
                )

            question_embed.set_footer(text="💫 The answer will be revealed in 60 seconds... 💫")

            try:
                await ctx.author.send(embed=question_embed)

                channel_embed = discord.Embed(
                    title="📨 Question Generated!",
                    description="I've sent you a DM with the question! Check your private messages.",
                    color=discord.Color.green()
                )
                channel_embed.set_image(url=self.dm_gif_url)
                channel_embed.set_footer(text="Made with ❤️ by Rohanpreet Singh Pathania")
                await ctx.send(embed=channel_embed)

                await asyncio.sleep(60)

                if 'correct_answer' in question_data:
                    answer_embed = discord.Embed(
                        title="✨ Answer Revealed! ✨",
                        color=discord.Color.gold()
                    )

                    correct_letter = question_data['correct_answer']
                    emoji = self.option_emojis.get(correct_letter, '✅')

                    answer_text = f"{emoji} The correct answer is {correct_letter}"
                    if 'explanation' in question_data:
                        answer_text += f"\n\n**Explanation:**\n{question_data['explanation']}"

                    answer_embed.description = answer_text
                    await ctx.author.send(embed=answer_embed)

            except discord.Forbidden:
                error_embed = discord.Embed(
                    title="❌ Cannot Send Private Message",
                    description="Please enable direct messages from server members:\n"
                                "Right-click the server icon → Privacy Settings → Enable direct messages",
                    color=discord.Color.red()
                )
                await ctx.send(embed=error_embed)

        except Exception as e:
            self.logger.error(f"Error sending question to DM: {str(e)}")
            await ctx.send("❌ An error occurred while sending the question.")

    @commands.command(name='chapters11')
    async def view_chapters_11(self, ctx, subject: str = None):
        """View chapters for Class 11 subjects"""
        try:
            if not subject:
                embed = discord.Embed(
                    title="📚 Available Subjects for Class 11",
                    description="Please specify a subject: !chapters11 <subject>",
                    color=discord.Color.blue()
                )
                subjects = list(self.chapters[11].keys())
                formatted_subjects = "\n".join([f"• {subj.title()}" for subj in subjects])
                embed.add_field(name="Subjects:", value=f"```{formatted_subjects}```")
                await ctx.send(embed=embed)
                return

            subject = subject.lower()
            if subject not in self.chapters[11]:
                await ctx.send(f"❌ Invalid subject. Available subjects: {', '.join(self.chapters[11].keys())}")
                return

            embed = discord.Embed(
                title=f"📖 Class 11 {subject.title()} Chapters",
                color=discord.Color.green()
            )

            chapter_list = self.chapters[11][subject]
            formatted_chapters = "\n".join([f"{i+1}. {chapter}" for i, chapter in enumerate(chapter_list)])

            embed.add_field(
                name="Chapters",
                value=f"```{formatted_chapters}```",
                inline=False
            )

            embed.set_footer(text=f"Use !11 {subject} <chapter_name> to get questions!")
            await ctx.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Error in view_chapters_11: {e}")
            await ctx.send("❌ An error occurred while fetching chapters. Please try again.")

    @commands.command(name='chapters12')
    async def view_chapters_12(self, ctx, subject: str = None):
        """View chapters for Class 12 subjects"""
        try:
            if not subject:
                embed = discord.Embed(
                    title="📚 Available Subjects for Class 12",
                    description="Please specify a subject: !chapters12 <subject>",
                    color=discord.Color.blue()
                )
                subjects = list(self.chapters[12].keys())
                formatted_subjects = "\n".join([f"• {subj.title()}" for subj in subjects])
                embed.add_field(name="Subjects:", value=f"```{formatted_subjects}```")
                await ctx.send(embed=embed)
                return

            subject = subject.lower()
            if subject not in self.chapters[12]:
                await ctx.send(f"❌ Invalid subject. Available subjects: {', '.join(self.chapters[12].keys())}")
                return

            embed = discord.Embed(
                title=f"📖 Class 12 {subject.title()} Chapters",
                color=discord.Color.green()
            )

            chapter_list = self.chapters[12][subject]
            formatted_chapters = "\n".join([f"{i+1}. {chapter}" for i, chapter in enumerate(chapter_list)])

            embed.add_field(
                name="Chapters",
                value=f"```{formatted_chapters}```",
                inline=False
            )

            embed.set_footer(text=f"Use !12 {subject} <chapter_name> to get questions!")
            await ctx.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Error in view_chapters_12: {e}")
            await ctx.send("❌ An error occurred while fetching chapters. Please try again.")

    @commands.command(name='help')
    async def help_command(self, ctx):
        """Show help information with fancy formatting"""
        help_embed = discord.Embed(
            title="📚 Educational Bot Help",
            description="Your personal study companion for Class 11 & 12!",
            color=discord.Color.blue()
        )

        # Main Commands Section
        commands_info = (
            "```ansi\n"
            "[1;34m┏━━━━━ Main Commands ━━━━━┓[0m\n"
            "[1;32m!11[0m - Get Class 11 Questions\n"
            "[1;32m!12[0m - Get Class 12 Questions\n"
            "[1;32m!subjects[0m - List All Subjects\n"
            "[1;32m!chapters11[0m - View Class 11 Chapters\n"
            "[1;32m!chapters12[0m - View Class 12 Chapters\n"
            "[1;32m!ping[0m - Check Bot Status\n"
            "[1;34m┗━━━━━━━━━━━━━━━━━━━━━━━┛[0m\n"
            "```"
        )
        help_embed.add_field(
            name="🎮 Available Commands",
            value=commands_info,
            inline=False
        )

        # Chapter Viewing Section
        chapter_info = (
            "```ansi\n"
            "[1;35m┏━━━━━ Chapter Commands ━━━━━┓[0m\n"
            "• !chapters11 <subject>\n"
            "  View chapters for Class 11 subject\n"
            "• !chapters12 <subject>\n"
            "  View chapters for Class 12 subject\n"
            "[1;35m┗━━━━━━━━━━━━━━━━━━━━━━━━━┛[0m\n"
            "```"
        )
        help_embed.add_field(
            name="📖 Chapter Viewing",
            value=chapter_info,
            inline=False
        )

        # Examples Section
        examples = (
            "```ansi\n"
            "[1;33m┏━━━━━ Examples ━━━━━┓[0m\n"
            "!11 physics waves\n"
            "!12 chemistry organic\n"
            "!chapters11 physics\n"
            "!chapters12 chemistry\n"
            "!subjects\n"
            "[1;33m┗━━━━━━━━━━━━━━━━━━━┛[0m\n"
            "```"
        )
        help_embed.add_field(
            name="📝 Example Usage",
            value=examples,
            inline=False
        )

        # Features Section
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

        # Creator Info Section
        creator_info = (
            "```ansi\n"
            "[0;35m┏━━━━━ Creator Information ━━━━━┓[0m\n"
            "[0;36m┃     Made with 💖 by:          ┃[0m\n"
            "[0;33m┃  Rohanpreet Singh Pathania   ┃[0m\n"
            "[0;36m┃     Language: Python 🐍      ┃[0m\n"
            "[0;35m┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛[0m\n"
            "