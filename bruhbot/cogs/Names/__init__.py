from .names import Names


async def setup(bot):
    await bot.add_cog(Names(bot))
