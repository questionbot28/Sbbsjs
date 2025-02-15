import discord
from discord.ext import commands
import google.generativeai as genai
import os
import logging
from typing import Dict, List, Optional
import time
from dotenv import load_dotenv
import aiohttp

load_dotenv()

class AIChat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger('discord_bot')
        self.conversations: Dict[int, List[dict]] = {}  # Store user conversations
        self.last_used: Dict[int, float] = {}  # Rate limiting
        self.rate_limit = 5  # Seconds between messages
        self.ai_channel_id = 1340150404775940210  # AI chat channel ID

        # Configure Gemini
        api_key = os.getenv('GOOGLE_AI_API_KEY')
        if not api_key:
            self.logger.error("GOOGLE_AI_API_KEY not found in environment variables")
            raise ValueError("GOOGLE_AI_API_KEY is required")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        self.logger.info("Gemini API configured successfully")

    async def _check_channel(self, ctx) -> bool:
        """Check if command is used in the AI chat channel"""
        if ctx.channel.id != self.ai_channel_id:
            await ctx.send(f"❌ AI chat commands can only be used in <#{self.ai_channel_id}>!")
            self.logger.warning(f"User attempted to use AI command in wrong channel: {ctx.channel.id}")
            return False
        return True

    def _format_compare(self, topic1: str, topic2: str, comparison: str) -> str:
        """Format the comparison response"""
        return f"""6️⃣ !compare {topic1} vs {topic2} – The Ultimate Face-Off!

⚖ Battle of the Concepts: {topic1} vs {topic2}

📌 Let's Compare:
{comparison}

🔍 Which one is better? It depends on the situation! Want a detailed breakdown? Type !explain {topic1} or !explain {topic2}.

🚀 Let's keep exploring!

---"""

    @commands.command(name="ask")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def ask(self, ctx, *, question: str):
        """Ask any question to the AI assistant"""
        if not await self._check_channel(ctx):
            return

        # Check rate limit
        user_id = ctx.author.id
        current_time = time.time()
        if user_id in self.last_used:
            time_diff = current_time - self.last_used[user_id]
            if time_diff < self.rate_limit:
                await ctx.send(f"⏳ Please wait {int(self.rate_limit - time_diff)} seconds before asking another question!")
                return

        async with ctx.typing():
            try:
                self.logger.info(f"Processing question from {ctx.author.name}: {question}")
                # Initialize conversation for new users
                if user_id not in self.conversations:
                    self.conversations[user_id] = []
                    chat = self.model.start_chat(history=[])
                    # Assuming system_prompt exists elsewhere,  or is not needed.
                    #chat.send_message(self.system_prompt) 
                else:
                    chat = self.model.start_chat(history=self.conversations[user_id])

                # Get AI response
                response = chat.send_message(question)

                # Update conversation history
                self.conversations[user_id].append({"role": "user", "parts": [question]})
                self.conversations[user_id].append({"role": "model", "parts": [response.text]})

                # Truncate conversation history if too long (keep last 20 messages)
                if len(self.conversations[user_id]) > 20:
                    self.conversations[user_id] = self.conversations[user_id][-20:]

                # Format the response
                formatted_response = self._format_response(question, response.text)

                # Create embed response
                embed = discord.Embed(
                    description=formatted_response,
                    color=discord.Color.blue()
                )
                embed.set_footer(text=f"Asked by {ctx.author.name}")

                # Send response
                await ctx.send(embed=embed)

                # Update rate limit
                self.last_used[user_id] = current_time
                self.logger.info(f"Successfully processed question from {ctx.author.name}")

            except Exception as e:
                self.logger.error(f"Error in AI response: {str(e)}")
                await ctx.send("❌ Sorry, I encountered an error while processing your question. Please try again later.")

    @commands.command(name="explain")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def explain(self, ctx, *, topic: str):
        """Get a detailed explanation of a topic"""
        if not await self._check_channel(ctx):
            return

        async with ctx.typing():
            try:
                self.logger.info(f"Generating explanation for topic: {topic}")
                prompt = f"""Provide a clear and detailed explanation of the following topic for a Class 11/12 student:
                Topic: {topic}

                Format your response to be:
                1. Clear and easy to understand
                2. Include relevant examples if applicable
                3. Break down complex concepts
                4. Include key points and takeaways"""

                response = self.model.generate_content(prompt)
                formatted_response = self._format_explanation(topic, response.text)

                embed = discord.Embed(
                    description=formatted_response,
                    color=discord.Color.green()
                )
                embed.set_footer(text=f"Explanation requested by {ctx.author.name}")
                await ctx.send(embed=embed)
                self.logger.info(f"Successfully generated explanation for {ctx.author.name}")

            except Exception as e:
                self.logger.error(f"Error in explanation: {str(e)}")
                await ctx.send("❌ Sorry, I couldn't generate an explanation. Please try again later.")

    @commands.command(name="summarize")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def summarize(self, ctx, *, text: str):
        """Summarize the provided text or link content"""
        if not await self._check_channel(ctx):
            return

        async with ctx.typing():
            try:
                # Check if input is a URL
                if text.startswith(('http://', 'https://')):
                    async with aiohttp.ClientSession() as session:
                        async with session.get(text) as response:
                            if response.status == 200:
                                content = await response.text()
                                # Basic HTML cleanup (you might want to use a proper HTML parser)
                                content = ' '.join(content.split())
                                source = text
                            else:
                                await ctx.send("❌ Could not access the provided URL.")
                                return
                else:
                    content = text
                    source = "Provided text"

                prompt = f"""Summarize the following content concisely while maintaining the key points:
                {content[:4000]}  # Limit content length

                Provide a clear and structured summary that:
                1. Captures the main ideas
                2. Highlights key points
                3. Maintains context
                4. Is easy to understand"""

                response = self.model.generate_content(prompt)
                formatted_response = self._format_summary(source, response.text)

                embed = discord.Embed(
                    description=formatted_response,
                    color=discord.Color.gold()
                )
                embed.set_footer(text=f"Summarized for {ctx.author.name}")
                await ctx.send(embed=embed)

            except Exception as e:
                self.logger.error(f"Error in summarization: {str(e)}")
                await ctx.send("❌ Sorry, I couldn't generate a summary. Please try again later.")

    @commands.command(name="solve")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def solve(self, ctx, *, problem: str):
        """Get a step-by-step solution for a problem"""
        if not await self._check_channel(ctx):
            return

        async with ctx.typing():
            try:
                prompt = f"""Solve this problem step by step for a Class 11/12 student:
                Problem: {problem}

                Provide:
                1. Clear step-by-step solution
                2. Explanations for each step
                3. A related fun fact or tip
                4. Alternative solution method if applicable"""

                response = self.model.generate_content(prompt)

                # Extract solution and generate a fun fact
                solution_text = response.text
                fun_fact_prompt = f"Give me a short, interesting fun fact related to this topic: {problem}"
                fun_fact_response = self.model.generate_content(fun_fact_prompt)
                fun_fact = fun_fact_response.text.strip()

                formatted_response = self._format_solution(problem, solution_text, fun_fact)

                embed = discord.Embed(
                    description=formatted_response,
                    color=discord.Color.blue()
                )
                embed.set_footer(text=f"Solution requested by {ctx.author.name}")
                await ctx.send(embed=embed)

            except Exception as e:
                self.logger.error(f"Error in problem solving: {str(e)}")
                await ctx.send("❌ Sorry, I couldn't solve this problem. Please try again later.")

    @commands.command(name="practice")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def practice(self, ctx, *, subject: str):
        """Generate practice questions for a subject"""
        if not await self._check_channel(ctx):
            return

        async with ctx.typing():
            try:
                prompt = f"""Generate 3 practice questions for a Class 11/12 student studying {subject}.
                Make questions that:
                1. Test different aspects of the subject
                2. Vary in difficulty
                3. Are clear and well-formulated
                4. Are relevant to NCERT curriculum"""

                response = self.model.generate_content(prompt)
                questions = response.text.strip().split('\n')
                if len(questions) < 3:
                    questions = questions + ["Sample question"] * (3 - len(questions))
                questions = questions[:3]  # Ensure exactly 3 questions

                formatted_response = self._format_practice(subject, questions)

                embed = discord.Embed(
                    description=formatted_response,
                    color=discord.Color.purple()
                )
                embed.set_footer(text=f"Practice questions for {ctx.author.name}")
                await ctx.send(embed=embed)

            except Exception as e:
                self.logger.error(f"Error generating practice questions: {str(e)}")
                await ctx.send("❌ Sorry, I couldn't generate practice questions. Please try again later.")

    @commands.command(name="clear_chat")
    async def clear_chat(self, ctx):
        """Clear your chat history with the AI"""
        if not await self._check_channel(ctx):
            return

        user_id = ctx.author.id
        if user_id in self.conversations:
            self.conversations.pop(user_id)
            await ctx.send("✅ Your chat history has been cleared!")
        else:
            await ctx.send("ℹ️ You don't have any chat history to clear!")

    @commands.command(name="aihelp")
    async def ai_help(self, ctx):
        """Show AI chat commands and guidelines"""
        if not await self._check_channel(ctx):
            return

        embed = discord.Embed(
            title="🤖 AI Chat Help",
            description="Get help with your studies using our AI assistant!",
            color=discord.Color.blue()
        )

        commands_info = """
        `!ask <question>` - Ask any question to the AI
        `!explain <topic>` - Get detailed explanation of a topic
        `!summarize <text/link>` - Get a summary of text or webpage
        `!solve <problem>` - Get step-by-step problem solutions
        `!practice <subject>` - Get practice questions
        `!clear_chat` - Clear your conversation history
        `!aihelp` - Show this help message
        `!compare <topic1> vs <topic2>` - Compare two topics
        """
        embed.add_field(name="📝 Commands", value=commands_info, inline=False)

        tips = """
        • Be specific in your questions
        • One question at a time works best
        • For complex topics, break them down
        • Use clear language
        • Wait 5 seconds between questions
        """
        embed.add_field(name="💡 Tips for Best Results", value=tips, inline=False)

        subjects = """
        • Physics
        • Chemistry
        • Mathematics
        • Biology
        • Computer Science
        • English
        And more from NCERT curriculum!
        """
        embed.add_field(name="📚 Supported Subjects", value=subjects, inline=False)

        await ctx.send(embed=embed)

    @commands.command(name="compare")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def compare(self, ctx, *, comparison: str):
        """Compare two topics"""
        if not await self._check_channel(ctx):
            return

        try:
            # Parse topics from the comparison string
            if " vs " not in comparison:
                await ctx.send("❌ Please use the format: !compare <topic1> vs <topic2>")
                return

            topic1, topic2 = comparison.split(" vs ", 1)
            topic1 = topic1.strip()
            topic2 = topic2.strip()

            async with ctx.typing():
                prompt = f"""Compare these two topics in the context of Class 11/12 education:
                Topic 1: {topic1}
                Topic 2: {topic2}

                Focus on:
                1. Key differences and similarities
                2. Use cases and applications
                3. Advantages and disadvantages
                4. Educational relevance"""

                response = self.model.generate_content(prompt)
                formatted_response = self._format_compare(topic1, topic2, response.text)

                embed = discord.Embed(
                    description=formatted_response,
                    color=discord.Color.blue()
                )
                embed.set_footer(text=f"Comparison requested by {ctx.author.name}")
                await ctx.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Error in comparison: {str(e)}")
            await ctx.send("❌ Sorry, I couldn't generate the comparison. Please try again later.")


    def _format_response(self, question: str, response: str) -> str:
        """Format the AI response with the specified template"""
        return f"""🤖 EduSphere bot
Hello there! I'm EduSphere, your AI study buddy. How can I assist you today?

> 📌 Your Question: {question}


🔍 Here's my response:
{response}

I'm here to help with NCERT Class 11 & 12 topics, problem-solving, and concept explanations. Feel free to ask anything!

📚 Need more details? Just ask! 🚀

---"""

    def _format_explanation(self, topic: str, explanation: str) -> str:
        """Format the explanation response"""
        return f"""📌 AI Concept Explanation

🔍 Topic: {topic}

📖 Explanation:
{explanation}

📌 Need more details? Ask me anything! 🚀

---"""

    def _format_summary(self, source: str, summary: str) -> str:
        """Format the summary response"""
        return f"""📌 AI Text Summarization

🔗 Source: {source}

📖 Summary:
{summary}

📌 Want a more detailed breakdown? Just ask!

---"""

    def _format_solution(self, problem: str, solution: str, fun_fact: str) -> str:
        """Format the solution response"""
        return f"""4️⃣ AI-Powered Problem Solver

🎯 Challenge Accepted! Let's break down your problem step by step.

📌 Problem: {problem}

🔢 Step-by-Step Solution:
{solution}

💡 Did You Know? {fun_fact}

📌 Need a different approach? Try !solve <problem> -method <method_name>

🚀 Keep Learning! Ask me another question!

---"""

    def _format_practice(self, subject: str, questions: list) -> str:
        """Format the practice questions response"""
        questions_text = "\n".join([f"🔹 Question {i+1}: {q}" for i, q in enumerate(questions)])
        return f"""5️⃣ Boost Your Learning!

📚 Test Your Knowledge in {subject}!

🔥 Challenge Questions:
{questions_text}

🔍 Want hints? Type !hint <question number>
✅ Need answers? Type !answer <question number>

📌 Let's practice more! Type !practice <new subject> 🚀

---"""

async def setup(bot):
    """Setup function for the cog"""
    await bot.add_cog(AIChat(bot))