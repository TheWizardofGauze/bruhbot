from .tts import TTS


async def setup(bot):
    await bot.add_cog(TTS(bot))
