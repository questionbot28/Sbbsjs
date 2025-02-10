{option_text}```", inline=False)

            # Add answer and explanation in the same DM
            if 'correct_answer' in question_data:
                answer_text = f"**Correct Answer:** {question_data['correct_answer']}"
                if 'explanation' in question_data:
                    answer_text += f"\n\n**Explanation:**\n{question_data['explanation']}"
                embed.add_field(name="Solution", value=answer_text, inline=False)

            # Try to send DM to user
            try:
                await ctx.author.send(embed=embed)

                # Send confirmation message in channel
                channel_embed = discord.Embed(
                    title="Question Generated!",
                    description="Check your private messages for the question and solution. If you do not receive the message, please unlock your private messages.",
                    color=discord.Color.green()
                )
                channel_embed.set_image(url=self.dm_gif_url)
                channel_embed.set_footer(text="Made by: Rohanpreet Singh Pathania")

                await ctx.send(embed=channel_embed)

            except discord.Forbidden:
                # If DM fails, send message in channel
                error_embed = discord.Embed(
                    title="❌ Cannot Send Private Message",
                    description="Please enable direct messages from server members to receive the question.\n"
                               "Right-click the server icon → Privacy Settings → Enable direct messages.",
                    color=discord.Color.red()
                )
                await ctx.send(embed=error_embed)

        except Exception as e:
            self.logger.error(f"Error sending question to DM: {str(e)}")
            await ctx.send("❌ An error occurred while sending the question.")

    async def cog_load(self):
        """Called when the cog is loaded"""
        self.logger.info("Education cog loaded successfully")

    @commands.command(name='help')
    async def help_command(self, ctx):
        """Show help information"""
        embed = discord.Embed(
            title="📚 Educational Bot Help",
            description="Here's how to use the educational bot:",
            color=discord.Color.blue()
        )

        embed.add_field(
            name="📘 Get Question for Class 11",
            value="```!11 <subject> [topic]```\nExample: !11 physics waves",
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
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def class_11(self, ctx, subject: str, topic: Optional[str] = None):
        """Get a question for class 11"""
        if ctx.channel.id != 1337669136729243658:
            await ctx.send("❌ This command can only be used in the designated channel!")
            return
        await self._handle_question_command(ctx, subject, topic, 11)

    @commands.command(name='12')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def class_12(self, ctx, subject: str, topic: Optional[str] = None):
        """Get a question for class 12"""
        if ctx.channel.id != 1337669207193682001:
            await ctx.send("❌ This command can only be used in the designated channel!")
            return
        await self._handle_question_command(ctx, subject, topic, 12)

    async def _handle_question_command(self, ctx, subject: str, topic: Optional[str], class_level: int):
        """Handle question generation for both class 11 and 12"""
        # Get lock for this user
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
                self._initialize_user_tracking(ctx.author.id, normalized_subject)

                # Generate question
                try:
                    question = await self._get_unique_question(
                        subject=normalized_subject,
                        topic=topic,
                        class_level=class_level,
                        user_id=str(ctx.author.id)
                    )

                    if not question:
                        await ctx.send("❌ Unable to generate a question at this time. Please try again.")
                        return

                    # Send question to DM instead of channel
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

    def _validate_subject(self, subject: str) -> tuple[bool, str]:
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

    async def _get_unique_question(self, subject: str, topic: str, class_level: int, user_id: str, max_attempts: int = 3):
        """Get a unique question for the user with retries"""
        for attempt in range(max_attempts):
            try:
                question = await self.question_generator.generate_question(
                    subject=subject,
                    topic=topic,
                    class_level=class_level,
                    user_id=user_id
                )

                if question:
                    return question
            except Exception as e:
                self.logger.error(f"Error generating question (attempt {attempt+1}/{max_attempts}): {str(e)}")
                if attempt == max_attempts - 1:
                    raise

        return None

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
        embed.add_field(name="Subjects:", value=f"```{subject_list}\n