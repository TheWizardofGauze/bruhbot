import json
import os

import discord
from redbot.core import commands


class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.file = f"{os.path.dirname(__file__)}\\games.json"

    # async def get_games(self):
    # get games and sort by platform

    async def get_color(self, ctx):
        if ctx.guild:
            color = ctx.guild.get_member(self.bot.user.id).top_role.color
            return color
        else:
            color = 0xE74C3C  # red
            return color

    @commands.is_owner()
    @commands.command()
    async def games(self, ctx):
        catl = []
        color = await self.get_color(ctx)
        with open(self.file) as f:
            data = json.load(f)
            for num, key in enumerate(data.keys()):
                key = str(num + 1) + ": " + key
                catl.append(key)
            content = "\n".join(catl)
            msg = discord.Embed(
                title="Choose a platform.", description=content, color=color
            )
            await ctx.send(embed=msg)
