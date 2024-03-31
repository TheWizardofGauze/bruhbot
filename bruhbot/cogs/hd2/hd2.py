from requests import get
import traceback

import discord
from redbot.core import commands, app_commands

from bruhbot import ErrorLogger


class HD2(commands.Cog):
    bot = commands.Bot(command_prefix="$", intents=discord.Intents.default())

    def __init__(self, bot):
        self.bot = bot
        self.api = "https://helldivers-2.fly.dev/api"

    def get_war_id(self):
        response = get(self.api)
        war_id = response.json()["current"]
        return war_id

    @commands.command()
    async def hd(self, ctx):
        async with ctx.typing():
            war_id = self.get_war_id()
            response = get(f"{self.api}/{war_id}/events")
            if response.status_code == 200:
                print("ok")
                await ctx.send(response.json()[0]["message"]["en"])
            else:
                print("nok")
                await ctx.send("Error")
