\n[2;34m✨ Welcome to the Staff Control Panel ✨[0m```",
            color=discord.Color.blue()
        )

        # Member Management Section with fancy formatting
        member_commands = (
            "```ansi\n"
            "[2;31m👥 Member Control Commands[0m\n\n"
            "[2;34m!mute[0m [2;37m<member> [reason][0m\n"
            "└─ Silence a member temporarily\n\n"
            "[2;34m!unmute[0m [2;37m<member>[0m\n"
            "└─ Restore member's voice\n\n"
            "[2;34m!kick[0m [2;37m<member> [reason][0m\n"
            "└─ Remove member from server\n\n"
            "[2;34m!ban[0m [2;37m<member> [reason][0m\n"
            "└─ Ban member from server\n\n"
            "[2;34m!unban[0m [2;37m<user_id>[0m\n"
            "└─ Remove member's ban\n"
            "```"
        )
        help_embed.add_field(
            name="🛡️ Member Controls",
            value=member_commands,
            inline=False
        )

        # Channel Management Section
        channel_commands = (
            "```ansi\n"
            "[2;31m💬 Channel Management[0m\n\n"
            "[2;34m!announce[0m [2;37m-r <role> <message>[0m\n"
            "└─ Send announcement with role ping\n"
            "  [2;37mExample: !announce -r @everyone New update![0m\n\n"
            "[2;34m!clear[0m [2;37m<amount>[0m\n"
            "└─ Clear specified messages\n"
            "```"
        )
        help_embed.add_field(
            name="📢 Channel Controls",
            value=channel_commands,
            inline=False
        )

        # System Commands Section
        system_commands = (
            "```ansi\n"
            "[2;31m⚙️ System Management[0m\n\n"
            "[2;34m!refresh[0m\n"
            "└─ Reload bot extensions\n\n"
            "[2;34m!ping[0m\n"
            "└─ Check bot latency\n"
            "