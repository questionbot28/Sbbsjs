{language}\n{response.text[:2000]}\n```",
                color=discord.Color.green()
            )

            await loading_msg.delete()
            await ctx.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Error in code command: {str(e)}")
            await loading_msg.edit(content="❌ An error occurred. Please try again.")

    @commands.command(name="debate")
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def debate(self, ctx, *, topic: str = None):
        """Generate a debate topic with pros and cons"""
        if not await self._check_channel(ctx):
            await ctx.send("❌ Please use this command in the ai-chat or bot-commands channel!")
            return

        loading_msg = await ctx.send("🤔 Generating debate topic...")

        try:
            if topic is None:
                topics = [
                    "Technology in Education",
                    "Homework in Schools",
                    "School Uniforms",
                    "Distance Learning",
                    "Standardized Testing",
                    "Year-Round School",
                    "Mobile Phones in Class",
                    "Grading System",
                    "School Start Times",
                    "Extra-Curricular Activities"
                ]
                topic = random.choice(topics)

            prompt = f"""Generate a balanced debate for the topic: {topic}
            Format the response as:

            Supporting Arguments:
            • [Point 1]
            • [Point 2]
            • [Point 3]

            Opposing Arguments:
            • [Point 1]
            • [Point 2]
            • [Point 3]
            """

            response = self.model.generate_content(prompt)

            if not response or not response.text:
                await loading_msg.edit(content="❌ No response received. Please try again.")
                return

            # Parse the response
            content = response.text
            try:
                supporting = content.split('Supporting Arguments:')[1].split('Opposing Arguments:')[0].strip()
                opposing = content.split('Opposing Arguments:')[1].strip()
            except IndexError:
                self.logger.error(f"Error parsing debate response: {content}")
                supporting = "Error parsing supporting arguments"
                opposing = "Error parsing opposing arguments"

            # Create embed
            embed = discord.Embed(
                title=f"🗣️ Debate Topic: {topic}",
                color=discord.Color.blue()
            )

            embed.add_field(
                name="🟢 Supporting Arguments",
                value=f"```{supporting[:1000]}```",
                inline=False
            )

            embed.add_field(
                name="🔴 Opposing Arguments",
                value=f"```{opposing[:1000]}