\n"
            "!mute <member> [reason] - Mute a member\n"
            "!unmute <member> - Unmute a member\n"
            "!kick <member> [reason] - Kick a member\n"
            "!ban <member> [reason] - Ban a member\n"
            "!unban <user_id> - Unban a member\n"
            "!clear <amount> - Clear messages\n"
            "```"
        )
        help_embed.add_field(
            name="🛡️ Moderation Commands",
            value=mod_commands,
            inline=False
        )

        # System Commands
        system_commands = (
            "```\n"
            "!announce <message> - Make an announcement\n"
            "!refresh - Reload bot extensions\n"
            "!ping - Check bot latency\n"
            "