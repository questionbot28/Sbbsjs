{options_text}```",
                    inline=False
                )

            question_embed.set_footer(text="The answer will be revealed in 60 seconds...")

            # Send question first
            try:
                await ctx.author.send(embed=question_embed)

                # Send confirmation in channel
                channel_embed = discord.Embed(
                    title="Question Generated!",
                    description="I've sent you a DM with the question! Check your private messages.",
                    color=discord.Color.green()
                )
                channel_embed.set_image(url=self.dm_gif_url)
                channel_embed.set_footer(text="Made by: Rohanpreet Singh Pathania")
                await ctx.send(embed=channel_embed)

                # Wait 60 seconds
                await asyncio.sleep(60)

                # Create and send answer embed
                if 'correct_answer' in question_data:
                    answer_embed = discord.Embed(
                        title="✨ Answer Revealed!",
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