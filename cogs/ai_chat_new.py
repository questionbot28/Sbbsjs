{debate_data['pros']}```",
                inline=False
            )

            embed.add_field(
                name="🔴 Opposing Arguments",
                value=f"```{debate_data['cons']}```",
                inline=False
            )

            embed.add_field(
                name="💡 Share Your Opinion",
                value="Type !opinion <your argument> to join the debate!",
                inline=False
            )

            embed.set_footer(text="Want another topic? Try !debate random")
            await loading_msg.delete()
            await ctx.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Error in debate command: {str(e)}")
            await ctx.send("❌ An error occurred while generating the debate. Please try again.")

    @commands.command(name="codinghelp")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def codinghelp(self, ctx, *, code: str):
        """Analyze and debug code"""
        if not await self._check_channel(ctx):
            return

        try:
            loading_msg = await ctx.send("💻 Analyzing your code...")

            prompt = f"""Analyze this code and provide:
            1. Code improvements
            2. Bug fixes if any
            3. Explanation of changes
            Format as JSON:
            {{
                "fixed_code": "improved version",
                "explanation": "detailed explanation"
            }}

            Code to analyze:
            {code}"""

            response = self.model.generate_content(prompt)
            try:
                analysis = json.loads(response.text)
            except json.JSONDecodeError:
                # Fallback if response is not valid JSON
                analysis = {
                    "fixed_code": code,
                    "explanation": response.text
                }

            embed = discord.Embed(
                title="💻 Code Analysis",
                color=discord.Color.blue()
            )

            embed.add_field(
                name="📌 Your Code",
                value=f"```python\n{code[:1000]}```",
                inline=False
            )

            embed.add_field(
                name="✅ Improved Code",
                value=f"```python\n{analysis['fixed_code'][:1000]}