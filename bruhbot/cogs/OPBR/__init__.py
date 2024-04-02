from .opbr import OPBR


async def setup(bot):
    await bot.add_cog(OPBR(bot))
