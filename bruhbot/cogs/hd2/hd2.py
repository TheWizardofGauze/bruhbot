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
        self.headers = {"Accept": "application/json", "User-Agent": "Bruhbot"}
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
                    text=f"REWARD: {reward} MEDALS",  # Reward type 1 is medals, maybe more rewards types in the future?
                    icon_url="attachment://medal.png",
                )
                embed.timestamp = datetime.now()
                return embed
            except Exception:
                owner = await self.bot.fetch_user(self.owner_id)
                await owner.send("Error logged in HD2.")
                ErrorLogger.run(traceback.format_exc())

        tags = ["<i=1>", "<i=3>", "</i>"]
        while True:
            try:
                with open(self.file, "r+", encoding="utf-8") as f:
                    data = json.load(f)
                    channel = self.bot.get_channel(data["servers"][0]["cid"])
                    for i in range(3):
                        try:
                            dresponse = get(
                                f"{self.api}/dispatches", headers=self.headers
                            )
                            if dresponse.status_code == 200:
                                derror = False
                                if dresponse.json() == []:
                                    ErrorLogger.run("dresponse returned empty.")
                                    break
                                for i, d in enumerate(reversed(dresponse.json())):
                                    if d["id"] > data["dispatch_id"]:
                                        with suppress(AttributeError):
                                            msg = d["message"]
                                            for tag in tags:
                                                msg = msg.replace(tag, "**")
                                            emb = await dembed(message=msg)
                                            await channel.send(embed=emb)
                                            if not d["id"] == data["dispatch_id"]:
                                                data["dispatch_id"] = d["id"]
                                                f.seek(0)
                                                json.dump(data, f, indent=4)
                                                f.truncate()

                                    else:
                                        continue
                                break
                            else:
                                derror = True
                                await asyncio.sleep(15)
                                continue
                        except Exception:
                            owner = await self.bot.fetch_user(self.owner_id)
                            await owner.send("Error logged in HD2.")
                            ErrorLogger.run(traceback.format_exc())
                            break
                    if derror is True and derror is not None:
                        owner = await self.bot.fetch_user(self.owner_id)
                        await owner.send(
                            f"dresponse status code {dresponse.status_code}"
                        )
                    for i in range(3):
                        try:
                            aresponse = get(
                                f"{self.api}/assignments", headers=self.headers
                            )
                            try:
                                aj = aresponse.json()
                                pindex = []
                                planets = []
                                if aresponse.status_code == 200:
                                    aerror = False
                                    if aj == []:
                                        ErrorLogger.run("aresponse returned empty.")
                                        break
                                    if aj[0]["id"] != data["assign_id"]:
                                        for t in aj[0]["tasks"]:
                                            pindex.append(t["values"][2])
                                        for p in pindex:
                                            presponse = get(
                                                f"{self.api}/planets/{p}",
                                                headers=self.headers,
                                            )
                                            planets.append(
                                                f"-{presponse.json()['name']}"
                                            )
                                        # title = aj[0]["title"]
                                        title = "MAJOR ORDER"
                                        briefing = aj[0]["briefing"]
                                        desc = aj[0]["description"]
                                        for tag in tags:
                                            # title = title.replace(tag, "**")
                                            briefing = briefing.replace(tag, "**")
                                            desc = desc.replace(tag, "**")
                                        reward = aj[0]["reward"]["amount"]
                                        morder = discord.File(
                                            f"{self.here}\\MajorOrder.png",
                                            filename="mologo.png",
                                        )
                                        micon = discord.File(
                                            f"{self.here}\\Medal.png",
                                            filename="medal.png",
                                        )
                                        emb = await aembed(
                                            title, briefing, desc, planets, reward
                                        )
                                        await channel.send(
                                            files=[morder, micon], embed=emb
                                        )
                                        data["assign_id"] = aj[0]["id"]
                                        f.seek(0)
                                        json.dump(data, f, indent=4)
                                        f.truncate()
                                        break
                                else:
                                    aerror = True
                                    await asyncio.sleep(15)
                                    continue
                            except exceptions.JSONDecodeError:
                                await asyncio.sleep(15)
                                continue
                        except Exception:
                            owner = await self.bot.fetch_user(self.owner_id)
                            await owner.send("Error logged in HD2.")
                            ErrorLogger.run(traceback.format_exc())
                            break
                    if aerror is True and aerror is not None:
                        owner = await self.bot.fetch_user(self.owner_id)
                        await owner.send(
                            f"aresponse status code {aresponse.status_code}"
                        )
                await asyncio.sleep(3600)
            except Exception:
                owner = await self.bot.fetch_user(self.owner_id)
                await owner.send("Error logged in HD2.")
                ErrorLogger.run(traceback.format_exc())
                await asyncio.sleep(15)
                continue

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.wait_until_ready()
        await self.update()

    @commands.command(hidden=True)
    @commands.is_owner()
    async def hd(self, ctx):
        await self.update()

    @app_commands.command(
        name="hd2status",
        description="Get current Galactic War status for Helldivers 2.",
    )
    @app_commands.checks.cooldown(1, 60, key=lambda i: (i.guild_id))
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
                    embed.add_field(name="Time Remaining:", value=time)
                    embed.add_field(name="Defense:", value=f"{liberation}%")
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
            for i in range(3):
                cresponse = get(f"{self.api}/campaigns", headers=self.headers)
                if cresponse.status_code == 200:
                    if cresponse.json() == []:
                        await interaction.followup.send("cresponse returned empty.")
                        return
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
                                        planet["event"]["maxHealth"]
                                        - int(planet["event"]["health"])
                                    )
                                    / int(planet["event"]["maxHealth"])
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
                    for i in range(3):
                        a2response = get(
                            f"{self.api}/assignments", headers=self.headers
                        )
                        if a2response.status_code == 200:
                            a2error = False
                            mo = []
                            if a2response.json() == []:
                                await interaction.followup.send(
                                    "aresponse returned empty. Unable to retrieve major orders."
                                )
                            else:
                                for t in a2response.json()[0]["tasks"]:
                                    mo.append(t["values"][2])
                            break
                        else:
                            a2error = True
                            await asyncio.sleep(15)
                            continue
                    if a2error is True and a2error is not None:
                        await interaction.followup.send(
                            f"aresponse status code {a2response.status_code}. Failed after 3 tries."
                        )
                        return
                    for i in range(3):
                        wresponse = get(f"{self.api}/war", headers=self.headers)
                        if wresponse.status_code == 200:
                            werror = False
                            if wresponse.json() == []:
                                await interaction.followup.send(
                                    "wresponse returned empty."
                                )
                                return
                            now = datetime.strptime(
                                wresponse.json()["now"], "%Y-%m-%dT%H:%M:%SZ"
                            )
                            break
                        else:
                            werror = True
                            await asyncio.sleep(15)
                            continue
                    if werror is True and werror is not None:
                        await interaction.followup.send(
                            f"wresponse status code {wresponse.status_code}. Failed after 3 tries."
                        )
                        return
                    embl = []
                    files = set()
                    selogo = discord.File(
                        f"{self.here}\\SuperEarth.png", filename="selogo.png"
                    )
                    alogo = discord.File(
                        f"{self.here}\\Automaton.png", filename="alogo.png"
                    )
                    tlogo = discord.File(
                        f"{self.here}\\Terminid.png", filename="tlogo.png"
                    )
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
                    return

                elif cresponse.status_code == 429:
                    await asyncio.sleep(15)
                    continue

            await interaction.followup.send(
                f"cresponse status code {cresponse.status_code}. Failed after 3 tries."
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
