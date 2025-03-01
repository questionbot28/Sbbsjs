import discord
from discord.ext import commands
import logging
import os
import pyttsx3
import asyncio
import json
from pathlib import Path

class VoiceCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger('discord_bot')
        self.user_languages = {}  # Store user language preferences
        self.voice_channel = None
        self.current_voice_client = None
        # Command channel restriction
        self.commands_channel_id = 1345245260393091145  # Updated channel ID
        # Store last AI responses
        self.last_responses = {}  # {user_id: last_response}

        # Ensure responses directory exists
        self.responses_dir = Path("voice_responses")
        self.responses_dir.mkdir(exist_ok=True)

    def get_response_path(self, user_id):
        """Get path for user's response file"""
        return self.responses_dir / f"response_{user_id}.wav"

    async def _check_channel(self, ctx):
        """Check if command is used in allowed channels"""
        if ctx.channel.id != self.commands_channel_id:
            await ctx.send(f"❌ Voice commands can only be used in <#{self.commands_channel_id}>!")
            return False
        return True

    @commands.command(name='setlang')
    async def set_language(self, ctx, lang_code: str):
        """Set preferred language for voice responses"""
        try:
            # Map language codes to pyttsx3 voices
            voice_mapping = {
                'en': 'english',
                'es': 'spanish',
                'fr': 'french',
                'de': 'german',
                'it': 'italian',
                'pt': 'portuguese'
            }

            if lang_code not in voice_mapping:
                supported_langs = ", ".join(voice_mapping.keys())
                await ctx.send(f"❌ Invalid language code. Supported languages: {supported_langs}")
                return

            # Store user's language preference
            self.user_languages[ctx.author.id] = lang_code
            await ctx.send(f"✅ Voice language set to: {voice_mapping[lang_code]}")
            self.logger.info(f"Set language {lang_code} for user {ctx.author.name}")

        except Exception as e:
            self.logger.error(f"Error setting language: {e}")
            await ctx.send("❌ Failed to set language preference.")

    @commands.command(name='explainvoice')
    @commands.cooldown(1, 30, commands.BucketType.user)  # 30 second cooldown
    async def explain_voice(self, ctx, *, text: str = None):
        """Explain text using voice in the user's preferred language"""
        try:
            # Check if command is used in the correct channel
            if not await self._check_channel(ctx):
                return

            # Check if user is in a voice channel
            if not ctx.author.voice:
                await ctx.send("❌ You must be in a voice channel to use this command!")
                return

            # Get user's preferred language (default to English)
            lang = self.user_languages.get(ctx.author.id, "en")

            # If no text provided, get last AI response
            if not text:
                if ctx.author.id not in self.last_responses:
                    await ctx.send("❌ Please provide text to explain!")
                    return
                text = self.last_responses[ctx.author.id]

            # Send status message
            status_msg = await ctx.send("🎵 Generating voice response...")

            try:
                # Generate voice response
                response_path = self.get_response_path(ctx.author.id)
                self.logger.info(f"Generating voice response to {response_path}")

                engine = pyttsx3.init()
                engine.setProperty('rate', 150)  # Speed of speech
                engine.setProperty('volume', 0.9)  # Volume (0.0 to 1.0)

                # Save to file
                engine.save_to_file(text, str(response_path))
                engine.runAndWait()

                self.logger.info("Voice file generated successfully")
                await status_msg.edit(content="🎵 Voice generated, connecting to voice channel...")

                # Connect to voice channel
                voice_channel = ctx.author.voice.channel
                if self.current_voice_client:
                    await self.current_voice_client.disconnect()

                try:
                    voice_client = await voice_channel.connect()
                    self.current_voice_client = voice_client
                    self.logger.info("Connected to voice channel successfully")
                except discord.ClientException:
                    await status_msg.edit(content="❌ I'm already in a voice channel! Please wait a moment.")
                    return
                except discord.Forbidden:
                    await status_msg.edit(content="❌ I need permission to join and speak in this voice channel!")
                    return

                # Wait a moment for file to be ready
                await asyncio.sleep(1)

                # Play the audio
                try:
                    if not os.path.exists(str(response_path)):
                        raise FileNotFoundError(f"Audio file not found at {response_path}")

                    self.logger.info("Starting audio playback")
                    audio_source = discord.FFmpegPCMAudio(
                        str(response_path),
                        options='-loglevel warning'
                    )
                    voice_client.play(audio_source)
                    await status_msg.edit(content="🔊 Playing voice response...")

                    # Wait for audio to finish
                    while voice_client.is_playing():
                        await asyncio.sleep(1)

                    self.logger.info("Audio playback completed")

                except Exception as e:
                    self.logger.error(f"Error playing audio: {e}")
                    await status_msg.edit(content="❌ Failed to play the voice response.")
                    if voice_client.is_connected():
                        await voice_client.disconnect()
                    if os.path.exists(str(response_path)):
                        os.remove(str(response_path))
                    return

                # Cleanup
                if voice_client.is_connected():
                    await voice_client.disconnect()
                if os.path.exists(str(response_path)):
                    os.remove(str(response_path))
                await status_msg.edit(content="✅ Voice explanation complete!")

            except Exception as e:
                self.logger.error(f"Error generating/playing voice: {e}")
                await status_msg.edit(content=f"❌ Failed to generate or play voice response: {str(e)}")
                if os.path.exists(str(response_path)):
                    os.remove(str(response_path))

        except Exception as e:
            self.logger.error(f"Error in explain_voice command: {e}")
            await ctx.send("❌ An error occurred while processing your request.")

    async def cleanup(self):
        """Cleanup function to be called when cog is unloaded"""
        try:
            # Disconnect from voice if connected
            if self.current_voice_client:
                await self.current_voice_client.disconnect()

            # Clean up any remaining response files
            for file in self.responses_dir.glob("response_*.wav"):
                file.unlink()
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")

async def setup(bot):
    cog = VoiceCommands(bot)
    await bot.add_cog(cog)
    logging.getLogger('discord_bot').info("VoiceCommands cog loaded successfully")