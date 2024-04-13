from .hd2 import HD2


async def setup(bot):
    await bot.add_cog(HD2(bot))
