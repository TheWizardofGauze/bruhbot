import asyncio
from collections import deque
import os
from tempfile import TemporaryFile
import traceback

import discord
from gtts import gTTS
from redbot.core import commands

from bruhbot import ErrorLogger


class TTS(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def say(self, ctx):
        """
        Text to Speech.

        I don't know what else to say.
        """
        queue = deque([])
        ffmpeg = f"{os.path.dirname(__file__)}\\ffmpeg\\ffmpeg.exe"
        msg = ctx.message.content[5:]
        try:
            vc = ctx.message.guild.voice_client
            if not vc.is_playing():
                text = gTTS(msg)
                f = TemporaryFile()
                text.write_to_fp(f)
                f.seek(0)
                vc.play(discord.FFmpegPCMAudio(f, pipe=True))
                vc.source = discord.PCMVolumeTransformer(vc.source)
                vc.source.volume = 100
            else:
                queue.append(msg)
                while vc.is_playing():
                    await asyncio.sleep(0.1)
                text = gTTS(msg)
                f = TemporaryFile()
                text.write_to_fp(f)
                f.seek(0)
                vc.play(discord.FFmpegPCMAudio(f, pipe=True))
                vc.source = discord.PCMVolumeTransformer(vc.source)
                vc.source.volume = 100
        except (TypeError, AttributeError):
            try:
                text = gTTS(msg)
                f = TemporaryFile()
                text.write_to_fp(f)
                f.seek(0)
                channel = ctx.message.author.voice.channel
                vc = await channel.connect()
                vc.play(discord.FFmpegPCMAudio(f, pipe=True))
                vc.source = discord.PCMVolumeTransformer(vc.source)
                vc.source.volume = 100
            except (TypeError, AttributeError):
                await ctx.send(
                    "Either you aren't in a voice channel or I'm a big dumb idiot, and I think I know which one it is..."
                )
                e = traceback.format_exc()
                ErrorLogger.run(e)
                return
