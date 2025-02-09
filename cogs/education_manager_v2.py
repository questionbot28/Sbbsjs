{formatted_subjects}```")
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

    @commands.command(name='ping')
    async def ping(self, ctx):
        """Check bot's latency"""
        latency = round(self.bot.latency * 1000)
        ping_embed = discord.Embed(
            title="🏓 Pong!",
            description=f"Bot latency: {latency}ms",
            color=discord.Color.green() if latency < 200 else discord.Color.orange()
        )

        if latency < 100:
            status = "🟢 Excellent"
        elif latency < 200:
            status = "🟡 Good"
        else:
            status = "🔴 Poor"

        ping_embed.add_field(
            name="Connection Quality",
            value=status,
            inline=False
        )
        await ctx.send(embed=ping_embed)

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