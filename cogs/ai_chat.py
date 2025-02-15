\n{code[:1000]}```",
                    inline=False
                )

                embed.add_field(
                    name="✅ Improved Code:",
                    value=f"```python\n{analysis.get('fixed_code', 'No improvements needed')[:1000]}```",
                    inline=False
                )

                embed.add_field(
                    name="📖 Explanation:",
                    value=analysis.get('explanation', 'No explanation provided')[:1024],
                    inline=False
                )

                await ctx.send(embed=embed)

            except Exception as e:
                self.logger.error(f"Error in codinghelp command: {str(e)}")
                await ctx.send("❌ Sorry, I couldn't analyze the code. Please try again later.")

    @commands.command(name="translate")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def translate(self, ctx, text: str, to_lang: str):
        """Translate text to specified language"""
        if not await self._check_channel(ctx):
            return

        async with ctx.typing():
            try:
                prompt = f"""Translate this text: "{text}" to {to_lang}
                Provide:
                1. Accurate translation
                2. Maintain original meaning
                3. Consider cultural context"""

                response = self.model.generate_content(prompt)
                translation = response.text.strip()

                embed = discord.Embed(
                    title="🌍 AI Translation",
                    color=discord.Color.blue()
                )

                embed.add_field(
                    name="📌 Original Text:",
                    value=f"📝 {text}",
                    inline=False
                )

                embed.add_field(
                    name=f"🌐 Translated to {to_lang}:",
                    value=f"🗣️ {translation}",
                    inline=False
                )

                embed.add_field(
                    name="🔍 Need Another Translation?",
                    value="Type !translate <text> to <new language> for more options!",
                    inline=False
                )

                await ctx.send(embed=embed)

            except Exception as e:
                self.logger.error(f"Error in translation: {str(e)}")
                await ctx.send("❌ Sorry, I couldn't translate the text. Please try again later.")

    @commands.command(name="compare")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def compare(self, ctx, *, comparison: str):
        """Compare two topics in a table format"""
        if not await self._check_channel(ctx):
            return

        try:
            if " vs " not in comparison:
                await ctx.send("❌ Please use the format: !compare <topic1> vs <topic2>")
                return

            topic1, topic2 = comparison.split(" vs ", 1)
            topic1 = topic1.strip()
            topic2 = topic2.strip()

            async with ctx.typing():
                prompt = f"""Compare these two topics for Class 11/12 education:
                Topic 1: {topic1}
                Topic 2: {topic2}

                Format your response as a comparison table with these aspects:
                1. Definition
                2. Key Features
                3. Applications
                4. Advantages
                5. Disadvantages
                6. Educational Importance

                For each aspect, provide direct comparisons between the topics.
                Format as: Aspect: Topic1 vs Topic2"""

                response = self.model.generate_content(prompt)

                # Create table header
                table = f"⚖️ Comparison: {topic1} vs {topic2}\n"
                table += "```\n"
                table += f"┌{'─' * 25}┬{'─' * 25}┐\n"
                table += f"│ {topic1:<25}│ {topic2:<25}│\n"
                table += f"├{'─' * 25}┼{'─' * 25}┤\n"

                # Parse response and build table
                aspects = response.text.split('\n')
                for aspect in aspects:
                    if ':' in aspect:
                        category, comparison = aspect.split(':', 1)
                        if 'vs' in comparison:
                            left, right = comparison.split('vs')
                            left = left.strip()[:25]
                            right = right.strip()[:25]
                            table += f"│ {left:<25}│ {right:<25}│\n"
                            table += f"├{'─' * 25}┼{'─' * 25}┤\n"

                table = table[:-len(f"├{'─' * 25}┼{'─' * 25}┤\n")]  # Remove last separator
                table += f"└{'─' * 25}┴{'─' * 25}┘\n