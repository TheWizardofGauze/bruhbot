import asyncio
import json
import os
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
        self.here = os.path.dirname(__file__)
        self.file = f"{self.here}\\hd2.json"

    async def get_war_id(self):
        response = get(self.api)
        if response.status_code == 200:
            war_id = response.json()["current"]
            return war_id

    async def update(self):
        try:

            async def embed(
                name: str,
                owner: str,
                liberation: str,
                players: str,
                logo: discord.File,
                hdlogo: discord.File,
                color: discord.Color,
            ):
                embed = discord.Embed(color=color)
                embed.title = name
                embed.description = f"{owner} control"
                embed.set_thumbnail(url="attachment://logo.png")
                embed.add_field(name="Liberation:", value=f"{liberation}%")
                embed.set_footer(
                    text=f"{players} Helldivers", icon_url="attachment://hdlogo.png"
                )
                return embed

            # while True
            war_id = await self.get_war_id()
            cresponse = get(f"{self.api}/{war_id}/status")
            if cresponse.status_code == 200:
                planets = []
                planetdata = {}
                for c in cresponse.json()["campaigns"]:
                    planets.append(c["planet"]["index"])
                for planet in planets:
                    presponse = get(f"{self.api}/{war_id}/planets/{planet}/status")
                    if presponse.status_code == 200:
                        name = presponse.json()["planet"]["name"]
                        lib = presponse.json()["liberation"]
                        owner = presponse.json()["owner"]
                        players = presponse.json()["players"]
                        planetdata.update(
                            {name: {"lib": lib, "owner": owner, "players": players}}
                        )
                with open(self.file, "r+", encoding="utf-8") as f:
                    data = json.load(f)
                    for server in data["servers"]:
                        channel = self.bot.get_channel(server["cid"])
                        async with channel.typing():
                            for planet in planetdata:
                                if planetdata[planet]["owner"] == "Humans":
                                    powner = "Super Earth"
                                    img = f"{self.here}\\SuperEarth.png"
                                    color = discord.Color.blue()
                                elif planetdata[planet]["owner"] == "Automaton":
                                    powner = "Automaton"
                                    img = f"{self.here}\\Automaton.png"
                                    color = 0xF11901
                                elif planetdata[planet]["owner"] == "Terminids":
                                    powner = "Terminid"
                                    img = f"{self.here}\\Terminid.png"
                                    color = 0xFEE75C
                                logo = discord.File(img, filename="logo.png")
                                hdlogo = discord.File(
                                    f"{self.here}\\Helldivers.png",
                                    filename="hdlogo.png",
                                )
                                emb = await embed(
                                    planet,
                                    powner,
                                    planetdata[planet]["lib"],
                                    planetdata[planet]["players"],
                                    logo,
                                    hdlogo,
                                    color,
                                )
                                await channel.send(files=[logo, hdlogo], embed=emb)
            else:
                owner = await self.bot.fetch_user(108105758578577408)
                await owner.send(cresponse.status_code)
                # asyncio.sleep(600)
        except Exception:
            ErrorLogger.run(traceback.format_exc())

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.wait_until_ready()
        owner = await self.bot.fetch_user(108105758578577408)
        await owner.send("TEST")

    @commands.command()
    async def hd(self, ctx):
        await self.update()
