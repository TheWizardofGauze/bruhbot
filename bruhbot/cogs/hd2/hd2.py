import asyncio
from contextlib import suppress
from datetime import datetime
import json
import os
from requests import get, exceptions
import traceback

from dateutil.relativedelta import relativedelta
import discord
from dotenv import load_dotenv
from redbot.core import commands, app_commands

from bruhbot import ErrorLogger


class HD2(commands.Cog):
    bot = commands.Bot(command_prefix="$", intents=discord.Intents.default())

    def __init__(self, bot):
        self.bot = bot
        self.api = "https://helldivers-2-dotnet.fly.dev/api/v1"
        self.here = os.path.dirname(__file__)
        self.file = f"{self.here}\\hd2.json"
        load_dotenv(os.path.abspath(".\\bruhbot\\.env"))
        self.owner_id = int(os.getenv("OWNER_ID"))

    async def update(self):
        async def dembed(
            message: str,
        ):
            try:
                embed = discord.Embed(color=0x2E3C4B)
                embed.description = message
                embed.timestamp = datetime.now()
                return embed
            except Exception:
                owner = await self.bot.fetch_user(self.owner_id)
                await owner.send("Error logged in HD2.")
                ErrorLogger.run(traceback.format_exc())

        async def aembed(
            title: str, briefing: str, description: str, planets: list, reward: str
        ):
            try:
                planet = "\n".join(planets)
                embed = discord.Embed(color=0xB5D9E9)
                embed.title = title
                embed.description = briefing
                embed.add_field(name=description, value=planet)
                embed.set_thumbnail(url="attachment://mologo.png")
                embed.set_footer(
                    text=f"REWARD: {reward} MEDALS",
                    icon_url="attachment://medal.png",
                )
                embed.timestamp = datetime.now()
                return embed
            except Exception:
                owner = await self.bot.fetch_user(self.owner_id)
                await owner.send("Error logged in HD2.")
                ErrorLogger.run(traceback.format_exc())

        while True:
            try:
                with open(self.file, "r+", encoding="utf-8") as f:
                    dump = False
                    data = json.load(f)
                    channel = self.bot.get_channel(data["servers"][0]["cid"])
                    dresponse = get(f"{self.api}/dispatches")
                    dbanner = discord.File(
                        f"{self.here}\\DispatchBanner.png", filename="dbanner.png"
                    )
                    if dresponse.status_code == 200:
                        for i, d in enumerate(reversed(dresponse.json())):
                            if d["id"] > data["dispatch_id"]:
                                with suppress(AttributeError):
                                    msg = d["message"].replace("<i=3>", "**")
                                    msg = msg.replace("</i>", "**")
                                    emb = await dembed(message=msg)
                                    await channel.send(file=dbanner, embed=emb)
                                    if not d["id"] == data["dispatch_id"]:
                                        dump = True
                                    data["dispatch_id"] = d["id"]
                            else:
                                continue
                    elif dresponse.status_code == 429:
                        await asyncio.sleep(10)
                        continue
                    else:
                        owner = await self.bot.fetch_user(self.owner_id)
                        await owner.send(
                            f"dresponse status code {dresponse.status_code}"
                        )
                    aresponse = get(f"{self.api}/assignments")
                    aj = aresponse.json()
                    pindex = []
                    planets = []
                    if aresponse.status_code == 200:
                        if aj[0]["id"] != data["assign_id"]:
                            try:
                                for t in aj[0]["tasks"]:
                                    pindex.append(t["values"][2])
                                for p in pindex:
                                    presponse = get(f"{self.api}/planets/{p}")
                                    planets.append(f"-{presponse.json()['name']}")
                                title = aj[0]["title"]
                                briefing = aj[0]["briefing"]
                                desc = aj[0]["description"]
                                reward = aj[0]["reward"]["amount"]
                                morder = discord.File(
                                    f"{self.here}\\MajorOrder.png",
                                    filename="mologo.png",
                                )
                                micon = discord.File(
                                    f"{self.here}\\Medal.png", filename="medal.png"
                                )
                                emb = await aembed(
                                    title, briefing, desc, planets, reward
                                )
                                await channel.send(files=[morder, micon], embed=emb)
                                data["assign_id"] = aj[0]["id"]
                                dump = True
                            except exceptions.JSONDecodeError:
                                await asyncio.sleep(10)
                                continue
                    elif aresponse.status_code == 429:
                        await asyncio.sleep(10)
                        continue
                    else:
                        owner = await self.bot.fetch_user(self.owner_id)
                        await owner.send(
                            f"aresponse status code {aresponse.status_code}"
                        )
                    if dump is True:
                        f.seek(0)
                        json.dump(data, f, indent=4)
                        f.truncate()
                await asyncio.sleep(3600)
            except Exception:
                owner = await self.bot.fetch_user(self.owner_id)
                await owner.send("Error logged in HD2.")
                ErrorLogger.run(traceback.format_exc())
                await asyncio.sleep(10)
                continue

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.wait_until_ready()
        await self.update()

    @commands.command()
    @commands.is_owner()
    async def hd(self, ctx):
        await self.update()

    @app_commands.command(
        name="hd2status",
        description="Get current Galactic War status for Helldivers 2.",
    )
    @app_commands.checks.cooldown(1, 300, key=lambda i: (i.guild_id))
    async def status(self, interaction: discord.Interaction):
        try:

            async def embed(
                name: str,
                owner: str,
                liberation: str,
                players: str,
                major: bool,
                time: str,
                color: discord.Color,
            ):
                embed = discord.Embed(color=color)
                embed.title = name
                embed.description = f"{owner} control"
                if owner == "Super Earth":
                    embed.add_field(name="Time Remaining", value=time)
                    # embed.add_field(name="Defense", value=f"{liberation}%")
                    embed.set_thumbnail(url="attachment://selogo.png")
                else:
                    embed.add_field(name="Liberation:", value=f"{liberation}%")
                    if owner == "Automaton":
                        embed.set_thumbnail(url="attachment://alogo.png")
                    elif owner == "Terminid":
                        embed.set_thumbnail(url="attachment://tlogo.png")
                    elif owner == "Illuminate":
                        embed.set_thumbnail(url="attachment://ilogo.png")
                embed.set_footer(
                    text=f"{players} Helldivers", icon_url="attachment://hdlogo.png"
                )
                if major is True:
                    embed.set_author(
                        name="MAJOR ORDER", icon_url="attachment://mologo.png"
                    )
                embed.timestamp = datetime.now()
                return embed

            await interaction.response.defer()
            cresponse = get(f"{self.api}/campaigns")
            if cresponse.status_code == 200:
                planets = []
                planetdata = {}
                for c in cresponse.json():
                    planets.append(c["planet"])
                for planet in planets:
                    index = planet["index"]
                    name = planet["name"]

                    owner = planet["currentOwner"]
                    if owner == "Humans":
                        end = datetime.strptime(
                            planet["event"]["endTime"], "%Y-%m-%dT%H:%M:%SZ"
                        )
                        lib = str(
                            (
                                int(
                                    planet["maxHealth"] - int(planet["event"]["health"])
                                )
                                / int(planet["maxHealth"])
                            )
                            * 100
                        )
                    else:
                        end = None
                        lib = str(
                            (
                                (int(planet["maxHealth"]) - int(planet["health"]))
                                / int(planet["maxHealth"])
                                * 100
                            )
                        )
                    players = planet["statistics"]["playerCount"]
                    planetdata.update(
                        {
                            name: {
                                "index": index,
                                "lib": lib,
                                "owner": owner,
                                "end": end,
                                "players": players,
                            }
                        }
                    )
                aresponse = get(f"{self.api}/assignments")
                if aresponse.status_code == 200:
                    mo = []
                    for t in aresponse.json()[0]["tasks"]:
                        mo.append(t["values"][2])
                else:
                    await interaction.followup.send(
                        f"aresponse status code {aresponse.status_code}",
                        ephemeral=True,
                    )
                wresponse = get(f"{self.api}/war")
                if wresponse.status_code == 200:
                    now = datetime.strptime(
                        wresponse.json()["now"], "%Y-%m-%dT%H:%M:%SZ"
                    )
                else:
                    await interaction.followup.send(
                        f"wresponse status code {wresponse.status_code}",
                        ephemeral=True,
                    )
                embl = []
                files = set()
                selogo = discord.File(
                    f"{self.here}\\SuperEarth.png", filename="selogo.png"
                )
                alogo = discord.File(
                    f"{self.here}\\Automaton.png", filename="alogo.png"
                )
                tlogo = discord.File(f"{self.here}\\Terminid.png", filename="tlogo.png")
                # ilogo = discord.File(f"{self.here}\\Illuminate.png",filename="ilogo.png")
                hdlogo = discord.File(
                    f"{self.here}\\Helldivers.png",
                    filename="hdlogo.png",
                )
                morder = discord.File(
                    f"{self.here}\\MajorOrder.png", filename="mologo.png"
                )
                files.add(hdlogo)
                for planet in planetdata:
                    if planetdata[planet]["index"] in mo:
                        major = True
                        files.add(morder)
                    else:
                        major = False
                    if planetdata[planet]["owner"] == "Humans":
                        powner = "Super Earth"
                        color = 0xB5D9E9
                        files.add(selogo)
                        rdelta = relativedelta(planetdata[planet]["end"], now)
                        time = f"{rdelta.days}D:{rdelta.hours}H:{rdelta.minutes}M:{rdelta.seconds}S"
                    elif planetdata[planet]["owner"] == "Automaton":
                        powner = "Automaton"
                        color = 0xFF6161
                        files.add(alogo)
                        time = None
                    elif planetdata[planet]["owner"] == "Terminids":
                        powner = "Terminid"
                        color = 0xFFB800
                        files.add(tlogo)
                        time = None
                    elif planetdata[planet]["owner"] == "Illuminate":  # SOON
                        powner = "Illuminate"
                        color = 0x000000
                        # files.add(ilogo)
                        time = None

                    emb = await embed(
                        planet,
                        powner,
                        planetdata[planet]["lib"],
                        planetdata[planet]["players"],
                        major,
                        time,
                        color,
                    )
                    embl.append(emb)
                await interaction.followup.send(files=files, embeds=embl)

            else:
                await interaction.followup.send(
                    f"cresponse status code {cresponse.status_code}",
                    ephemeral=True,
                )
                return
        except Exception:
            await interaction.followup.send("Error logged in HD2.")
            ErrorLogger.run(traceback.format_exc())

    @status.error
    async def status_error(self, interaction: discord.Interaction, error):
        if isinstance(error, commands.CommandOnCooldown):
            await interaction.response.send(
                f"Command on cooldown, try again in {error.retry_after: .0f} seconds.",
                ephemeral=True,
            )
