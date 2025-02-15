{code}
            ```

            Format your response as:
            1. Code Analysis:
               • Issues found
               • Suggested fixes

            2. Explanation:
               • What the code does
               • How it works

            3. Optimizations:
               • Performance tips
               • Best practices
            """

            response = self.gemini.generate_content(prompt)

            if not response or not response.text:
                await loading_msg.edit(content="❌ Failed to analyze code. Please try again.")
                return

            # Create code help embed
            embed = discord.Embed(
                title="💻 Code Analysis",
                color=discord.Color.blue()
            )

            content = response.text
            sections = content.split('\n\n')

            for section in sections:
                if '1. Code Analysis:' in section:
                    embed.add_field(
                        name="🔍 Analysis",
                        value=section.replace('1. Code Analysis:', '').strip(),
                        inline=False
                    )
                elif '2. Explanation:' in section:
                    embed.add_field(
                        name="📚 Explanation",
                        value=section.replace('2. Explanation:', '').strip(),
                        inline=False
                    )
                elif '3. Optimizations:' in section:
                    embed.add_field(
                        name="⚡ Optimizations",
                        value=section.replace('3. Optimizations:', '').strip(),
                        inline=False
                    )

            embed.set_footer(text="💡 Tip: Use !codegen to generate improved code")

            await loading_msg.delete()
            await ctx.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Error in codehelp command: {str(e)}")
            await loading_msg.edit(content="❌ An error occurred while analyzing the code.")

    @commands.command(name="codegen")
    @commands.cooldown(1, 20, commands.BucketType.user)
    async def codegen(self, ctx, *, prompt: str):
        """Generate code based on user prompt"""
        if not await self._check_channel(ctx):
            await ctx.send(f"❌ Please use this command in the AI chat channel! <#{self.ai_channel_id}>")
            return

        loading_msg = await ctx.send("💻 Generating code...")

        try:
            # Use OpenAI for code generation
            response = self.openai.chat.completions.create(
                model="gpt-4",  # Using GPT-4 for better code generation
                messages=[
                    {"role": "system", "content": "You are an expert programmer. Generate clean, well-documented code with explanations."},
                    {"role": "user", "content": f"Generate code for: {prompt}. Include comments and explanation."}
                ],
                temperature=0.7,
                max_tokens=1500
            )

            if not response.choices:
                await loading_msg.edit(content="❌ Code generation failed. Please try again.")
                return

            code_response = response.choices[0].message.content

            # Split into code and explanation
            parts = code_response.split('\n\n')
            code = ""
            explanation = ""

            for part in parts:
                if part.strip().startswith('```'):
                    code = part
                else:
                    explanation += part + '\n'

            # Create code embed
            embed = discord.Embed(
                title="💻 Generated Code",
                description=f"Here's the code for: {prompt}",
                color=discord.Color.green()
            )

            if code:
                embed.add_field(
                    name="📝 Code",
                    value=code[:1024],
                    inline=False
                )

            if explanation:
                embed.add_field(
                    name="📚 Explanation",
                    value=explanation[:1024],
                    inline=False
                )

            embed.set_footer(text="💡 Tip: Use !codehelp for debugging assistance")

            await loading_msg.delete()
            await ctx.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Error in codegen command: {str(e)}")
            await loading_msg.edit(content="❌ An error occurred during code generation.")

    @commands.command(name="translate")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def translate(self, ctx, *, text: str):
        """Translate text to specified language"""
        if not await self._check_channel(ctx):
            await ctx.send(f"❌ Please use this command in the AI chat channel! <#{self.ai_channel_id}>")
            return

        # Check for correct format
        match = re.match(r'(.+?)\s+to\s+(\w+)$', text, re.IGNORECASE)
        if not match:
            await ctx.send("❌ Please use the format: `!translate <text> to <language>`")
            return

        text_to_translate, target_language = match.groups()
        loading_msg = await ctx.send(f"🌍 Translating to {target_language}...")

        try:
            prompt = f"""Translate this text to {target_language}:
            Text: {text_to_translate}

            Provide:
            1. Translation
            2. Pronunciation (if applicable)
            3. Any cultural notes or context
            """

            response = self.gemini.generate_content(prompt)

            if not response or not response.text:
                await loading_msg.edit(content="❌ Translation failed. Please try again.")
                return

            # Create translation embed
            embed = discord.Embed(
                title="🌍 Translation",
                color=discord.Color.blue()
            )

            embed.add_field(
                name="📝 Original Text",
                value=text_to_translate,
                inline=False
            )

            translation_text = response.text
            sections = translation_text.split('\n\n')

            for section in sections:
                if section.startswith('1. '):
                    embed.add_field(
                        name=f"🔤 {target_language.title()} Translation",
                        value=section.replace('1. ', '').strip(),
                        inline=False
                    )
                elif section.startswith('2. '):
                    embed.add_field(
                        name="🗣️ Pronunciation",
                        value=section.replace('2. ', '').strip(),
                        inline=False
                    )
                elif section.startswith('3. '):
                    embed.add_field(
                        name="💡 Cultural Notes",
                        value=section.replace('3. ', '').strip(),
                        inline=False
                    )

            await loading_msg.delete()
            await ctx.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Error in translate command: {str(e)}")
            await loading_msg.edit(content="❌ An error occurred during translation.")

    @commands.command(name="ask")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def ask(self, ctx, *, question: str):
        """Ask AI any question"""
        if not await self._check_channel(ctx):
            await ctx.send(f"❌ Please use this command in the AI chat channel! <#{self.ai_channel_id}>")
            return

        async with ctx.typing():
            try:
                response = self.gemini.generate_content(question)
                if response and response.text:
                    # Create response embed
                    embed = discord.Embed(
                        title="🤔 Answer",
                        description=response.text[:4096],
                        color=discord.Color.blue()
                    )
                    embed.set_footer(text="💡 Tip: Use !explain for more detailed explanations")
                    await ctx.send(embed=embed)
                else:
                    await ctx.send("❌ No response received. Please try again.")
            except Exception as e:
                self.logger.error(f"Error in ask command: {str(e)}")
                await ctx.send("❌ An error occurred while processing your question.")

    @commands.command(name="explain")
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def explain(self, ctx, *, topic: str):
        """Get detailed explanation of a topic"""
        if not await self._check_channel(ctx):
            await ctx.send(f"❌ Please use this command in the AI chat channel! <#{self.ai_channel_id}>")
            return

        loading_msg = await ctx.send("🎓 Generating explanation...")

        try:
            prompt = f"""Explain this topic in detail:
            Topic: {topic}

            Format your response as:
            📚 Overview:
            [Brief introduction]

            🔑 Key Points:
            • Point 1
            • Point 2
            • Point 3

            💡 Examples:
            [Practical examples]

            🔗 Related Concepts:
            [List related topics]
            """

            response = self.gemini.generate_content(prompt)

            if not response or not response.text:
                await loading_msg.edit(content="❌ Explanation failed. Please try again.")
                return

            # Create explanation embed
            embed = discord.Embed(
                title=f"📚 {topic}",
                color=discord.Color.blue()
            )

            content = response.text
            sections = content.split('\n\n')

            for section in sections:
                if '📚 Overview:' in section:
                    embed.add_field(
                        name="📚 Overview",
                        value=section.replace('📚 Overview:', '').strip(),
                        inline=False
                    )
                elif '🔑 Key Points:' in section:
                    embed.add_field(
                        name="🔑 Key Points",
                        value=section.replace('🔑 Key Points:', '').strip(),
                        inline=False
                    )
                elif '💡 Examples:' in section:
                    embed.add_field(
                        name="💡 Examples",
                        value=section.replace('💡 Examples:', '').strip(),
                        inline=False
                    )
                elif '🔗 Related Concepts:' in section:
                    embed.add_field(
                        name="🔗 Related Concepts",
                        value=section.replace('🔗 Related Concepts:', '').strip(),
                        inline=False
                    )

            embed.set_footer(text="💡 Tip: Use !compare to compare this with another topic")

            await loading_msg.delete()
            await ctx.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Error in explain command: {str(e)}")
            await loading_msg.edit(content="❌ An error occurred while generating the explanation.")

    @commands.command(name="compare")
    @commands.cooldown(1, 20, commands.BucketType.user)
    async def compare(self, ctx, *, topics: str):
        """Compare two topics or concepts"""
        if not await self._check_channel(ctx):
            await ctx.send(f"❌ Please use this command in the AI chat channel! <#{self.ai_channel_id}>")
            return

        # Extract topics using regex
        match = re.match(r'(.+?)\s+(?:vs|versus)\s+(.+)', topics, re.IGNORECASE)
        if not match:
            await ctx.send("❌ Please use the format: `!compare <topic1> vs <topic2>`")
            return

        topic1, topic2 = match.groups()
        loading_msg = await ctx.send(f"⚖️ Comparing {topic1} vs {topic2}...")

        try:
            prompt = f"""Compare these topics in detail:
            Topic 1: {topic1}
            Topic 2: {topic2}

            Format your response as:
            📊 Key Differences:
            • Point 1
            • Point 2
            • Point 3

            💪 Strengths of {topic1}:
            • Point 1
            • Point 2

            💪 Strengths of {topic2}:
            • Point 1
            • Point 2

            🎯 Best Use Cases:
            {topic1}: [cases]
            {topic2}: [cases]
            """

            response = self.gemini.generate_content(prompt)

            if not response or not response.text:
                await loading_msg.edit(content="❌ Comparison failed. Please try again.")
                return

            # Create comparison embed
            embed = discord.Embed(
                title=f"⚖️ Comparing: {topic1} vs {topic2}",
                color=discord.Color.blue()
            )

            content = response.text
            sections = content.split('\n\n')

            for section in sections:
                if '📊 Key Differences:' in section:
                    embed.add_field(
                        name="📊 Key Differences",
                        value=section.replace('📊 Key Differences:', '').strip(),
                        inline=False
                    )
                elif f'💪 Strengths of {topic1}:' in section:
                    embed.add_field(
                        name=f"💪 {topic1} Strengths",
                        value=section.replace(f'💪 Strengths of {topic1}:', '').strip(),
                        inline=True
                    )
                elif f'💪 Strengths of {topic2}:' in section:
                    embed.add_field(
                        name=f"💪 {topic2} Strengths",
                        value=section.replace(f'💪 Strengths of {topic2}:', '').strip(),
                        inline=True
                    )
                elif '🎯 Best Use Cases:' in section:
                    embed.add_field(
                        name="🎯 Best Use Cases",
                        value=section.replace('🎯 Best Use Cases:', '').strip(),
                        inline=False
                    )

            embed.set_footer(text=f"💡 Tip: Use !explain {topic1} or !explain {topic2} for more details")

            await loading_msg.delete()
            await ctx.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Error in compare command: {str(e)}")
            await loading_msg.edit(content="❌ An error occurred during comparison.")

    @commands.command(name="debate")
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def debate(self, ctx, *, topic: str = None):
        """Generate a debate topic with pros and cons"""
        if not await self._check_channel(ctx):
            await ctx.send(f"❌ Please use this command in the AI chat channel! <#{self.ai_channel_id}>")
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

            response = self.gemini.generate_content(prompt)

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