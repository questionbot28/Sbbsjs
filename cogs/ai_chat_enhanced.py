
import discord
from discord.ext import commands
import json
import logging
import os
import random
import google.generativeai as genai

class AIChatEnhanced(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger('discord_bot')
        # Initialize Google AI model
        genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
        self.model = genai.GenerativeModel('gemini-pro')

    async def _check_channel(self, ctx):
        """Check if command is used in allowed channel"""
        if isinstance(ctx.channel, discord.DMChannel):
            return True
        allowed_channels = ['ai-chat', 'bot-commands']
        return ctx.channel.name in allowed_channels

    @commands.command(name="aihelp")
    async def aihelp(self, ctx):
        """Show AI commands help"""
        embed = discord.Embed(
            title="🤖 AI Commands Help",
            description="Here are all available AI commands:",
            color=discord.Color.blue()
        )
        
        commands = """
        `!debate <topic>` - Start a debate on any topic
        `!debate` - Get a random debate topic
        `!ask <question>` - Ask AI any question
        `!explain <topic>` - Get detailed explanation
        `!summarize <text>` - Summarize long text
        `!translate <text> <language>` - Translate text
        `!code <language> <prompt>` - Generate code
        """
        
        embed.add_field(name="Available Commands", value=commands, inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="ask")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def ask(self, ctx, *, question: str):
        """Ask AI any question"""
        if not await self._check_channel(ctx):
            return
            
        async with ctx.typing():
            try:
                response = self.model.generate_content(question)
                if response and response.text:
                    await ctx.reply(response.text[:2000])
                else:
                    await ctx.send("❌ No response received. Please try again.")
            except Exception as e:
                self.logger.error(f"Error in ask command: {str(e)}")
                await ctx.send(f"❌ An error occurred: {str(e)}")

    @commands.command(name="explain")
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def explain(self, ctx, *, topic: str):
        """Get detailed explanation of a topic"""
        if not await self._check_channel(ctx):
            return

        loading_msg = await ctx.send("🤔 Generating explanation...")
        try:
            prompt = f"Explain this topic in detail but concisely: {topic}"
            response = self.model.generate_content(prompt)
            if not response or not response.text:
                await loading_msg.edit(content="❌ No response received. Please try again.")
                return
            
            embed = discord.Embed(
                title=f"📚 {topic}",
                description=response.text[:4096],
                color=discord.Color.green()
            )
            
            await loading_msg.delete()
            await ctx.send(embed=embed)
        except Exception as e:
            self.logger.error(f"Error in explain command: {str(e)}")
            await loading_msg.edit(content="❌ An error occurred. Please try again.")

    @commands.command(name="summarize")
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def summarize(self, ctx, *, text: str):
        """Summarize long text"""
        if not await self._check_channel(ctx):
            return

        try:
            prompt = f"Summarize this text concisely: {text}"
            response = self.model.generate_content(prompt)
            
            embed = discord.Embed(
                title="📝 Summary",
                description=response.text[:2000],
                color=discord.Color.blue()
            )
            
            await ctx.send(embed=embed)
        except Exception as e:
            self.logger.error(f"Error in summarize command: {str(e)}")
            await ctx.send("❌ An error occurred. Please try again.")

    @commands.command(name="translate")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def translate(self, ctx, text: str, to_lang: str):
        """Translate text to specified language"""
        if not await self._check_channel(ctx):
            return

        try:
            prompt = f"Translate this text: '{text}' to {to_lang} language. Only provide the translation, nothing else."
            response = self.model.generate_content(prompt)
            
            if not response or not response.text:
                await ctx.send("❌ No response received from AI. Please try again.")
                return
                
            embed = discord.Embed(
                title="🌍 Translation",
                color=discord.Color.blue()
            )
            
            embed.add_field(name="Original", value=text, inline=False)
            embed.add_field(name=f"Translated to {to_lang}", value=response.text, inline=False)
            
            await ctx.send(embed=embed)
        except Exception as e:
            self.logger.error(f"Error in translate command: {str(e)}")
            await ctx.send("❌ An error occurred. Please try again.")

    @commands.command(name="code")
    @commands.cooldown(1, 20, commands.BucketType.user)
    async def code(self, ctx, language: str, *, prompt: str):
        """Generate code based on prompt"""
        if not await self._check_channel(ctx):
            return

        loading_msg = await ctx.send("💻 Generating code...")
        try:
            prompt = f"Write {language} code for: {prompt}. Provide brief explanation."
            response = self.model.generate_content(prompt)
            
            embed = discord.Embed(
                title=f"💻 Generated {language.capitalize()} Code",
                description=f"```{language}\n{response.text[:2000]}```",
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
            return

        loading_msg = await ctx.send("🤔 Generating debate topic...")

        try:
            if topic is None:
                topics = ["Technology in Education", "Homework", "School Uniforms", 
                         "Distance Learning", "Standardized Testing"]
                topic = random.choice(topics)

            prompt = f"""Generate a balanced debate for the topic: {topic}
            Provide:
            1. Clear title
            2. Supporting arguments (pros)
            3. Opposing arguments (cons)
            Keep each side's arguments concise and clear."""

            response = self.model.generate_content(prompt)
            debate_text = response.text

            debate_data = {
                'title': topic,
                'pros': debate_text.split('Pros:')[1].split('Cons:')[0].strip(),
                'cons': debate_text.split('Cons:')[1].strip()
            }

            embed = discord.Embed(
                title=f"🗣️ Debate Topic: {debate_data['title']}",
                color=discord.Color.blue()
            )

            embed.add_field(
                name="🟢 Supporting Arguments",
                value=f"```{debate_data['pros']}```",
                inline=False
            )

            embed.add_field(
                name="🔴 Opposing Arguments",
                value=f"```{debate_data['cons']}```",
                inline=False
            )

            await loading_msg.delete()
            await ctx.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Error in debate command: {str(e)}")
            await loading_msg.edit(content="❌ An error occurred. Please try again.")

async def setup(bot):
    await bot.add_cog(AIChatEnhanced(bot))
