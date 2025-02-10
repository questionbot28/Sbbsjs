\n"
            "[2;31m🔇 Member Control[0m\n"
            "[2;34m!mute[0m [2;37m<member> [reason][0m - Silence a member\n"
            "[2;34m!unmute[0m [2;37m<member>[0m - Restore member's voice\n"
            "[2;34m!kick[0m [2;37m<member> [reason][0m - Remove from server\n"
            "[2;34m!ban[0m [2;37m<member> [reason][0m - Ban from server\n"
            "[2;34m!unban[0m [2;37m<user_id>[0m - Remove ban\n"
            "```"
        )
        help_embed.add_field(
            name="👥 Member Management",
            value=member_commands,
            inline=False
        )

        # Channel Management
        channel_commands = (
            "```ansi\n"
            "[2;31m📢 Channel Control[0m\n"
            "[2;34m!clear[0m [2;37m<amount>[0m - Clear messages\n"
            "[2;34m!announce[0m [2;37m-r <role> <message>[0m - Make announcement\n"
            "[2;37m  Example: !announce -r @everyone New update![0m\n"
            "```"
        )
        help_embed.add_field(
            name="💬 Channel Management",
            value=channel_commands,
            inline=False
        )

        # System Commands
        system_commands = (
            "```ansi\n"
            "[2;31m⚙️ System Control[0m\n"
            "[2;34m!refresh[0m - Reload bot extensions\n"
            "[2;34m!ping[0m - Check bot latency\n"
            "