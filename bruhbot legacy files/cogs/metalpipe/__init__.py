from .metalpipe import Metalpipe


async def setup(bot):
    await bot.add_cog(Metalpipe())
