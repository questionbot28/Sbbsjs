{chapter_list}```",
                inline=False
            )
        else:
            # Show chapters for both classes
            for level in [11, 12]:
                chapters = self.subjects_data[subject][level]
                chapter_list = "\n".join([f"{i+1}. {chapter}" for i, chapter in enumerate(chapters)])

                embed.add_field(
                    name=f"Class {level} Chapters:",
                    value=f"```{chapter_list}