import asyncio
from contextlib import suppress
from datetime import datetime, UTC, timezone
import json
import os
import traceback
import typing

from aiohttp import ClientSession
from dateutil.relativedelta import relativedelta
import discord
from dotenv import load_dotenv
from redbot.core import commands, app_commands

from bruhbot import ErrorLogger


class HD2(commands.Cog):
    bot = commands.Bot(command_prefix="$", intents=discord.Intents.default())

    def __init__(self, bot):
        self.bot = bot
        self.api = "https://api.helldivers2.dev/api/v1"
        self.headers = {
            "Accept": "application/json",
            "User-Agent": "Bruhbot",
            "X-Super-Client": "Bruhbot",
            "X-Super-Contact": "gh/TheWizardofGauze",
        }
        self.here = os.path.dirname(__file__)
        self.file = f"{self.here}\\hd2.json"
        load_dotenv(os.path.abspath(".\\bruhbot\\.env"))
        self.owner_id = int(os.getenv("OWNER_ID"))

    hd2 = app_commands.Group(name="hd2", description="...")

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
            title: str,
            briefing: str,
            description: str,
            objectives: list,
            reward: str,
            expire: int,
        ):
            try:
                objective = "\n".join(objectives)
                embed = discord.Embed(color=0xB5D9E9)
                embed.title = title
                embed.description = briefing
                embed.add_field(name=description, value=objective)
                embed.add_field(name="Expires:", value=f"<t:{expire}:R>", inline=False)
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
                    async with ClientSession(headers=self.headers) as session:
                        for i in range(3):  # dresponse
                            try:
                                async with session.get(f"{self.api}/dispatches") as dresponse:
                                    if dresponse.status == 200:
                                        derror = False
                                        dj = await dresponse.json()
                                        if dj == []:
                                            ErrorLogger.run("dresponse returned empty.")
                                            break
                                        for i, d in enumerate(reversed(dj)):
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
                                        continue
                            except Exception:
                                owner = await self.bot.fetch_user(self.owner_id)
                                await owner.send("Error logged in HD2.")
                                ErrorLogger.run(traceback.format_exc())
                                break
                        if derror is True and derror is not None:
                            owner = await self.bot.fetch_user(self.owner_id)
                            await owner.send(f"dresponse status code {dresponse.status}")
                    await asyncio.sleep(0)
                    async with ClientSession(headers=self.headers) as session:
                        for i in range(3):  # aresponse
                            try:
                                async with session.get(f"{self.api}/assignments") as aresponse:
                                    try:
                                        objectives = []
                                        if aresponse.status == 200:
                                            aerror = False
                                            aj = await aresponse.json()
                                            if aj == []:
                                                ErrorLogger.run("aresponse returned empty.")
                                                break
                                            aj = aj[0]
                                            task = aj["tasks"][0]
                                            if aj["id"] != data["assign_id"]:
                                                if task["type"] == 3:
                                                    objectives.append(f"{task['values'][2]:,}")
                                                elif task["type"] == 12:
                                                    objectives.append(str(task["values"][0]))
                                                else:
                                                    pindex = []
                                                    for t in aj["tasks"]:
                                                        pindex.append(t["values"][2])
                                                    for i in range(3):
                                                        async with session.get(f"{self.api}/planets") as presponse:
                                                            if presponse.status == 200:
                                                                perror = False
                                                                pj = await presponse.json()
                                                                for p in pj:
                                                                    if p["index"] in pindex:
                                                                        objectives.append(f"-{p['name']}")
                                                                break
                                                            else:
                                                                perror = True
                                                                await asyncio.sleep(15)
                                                                continue
                                                    if perror is True and perror is not None:
                                                        owner = await self.bot.fetch_user(self.owner_id)
                                                        await owner.send(f"presponse status code {presponse.status}")
                                                        return
                                                title = aj["title"]
                                                briefing = aj["briefing"]
                                                desc = aj["description"]
                                                exp = round(
                                                    datetime.strptime(
                                                        aj["expiration"][:19].strip(),
                                                        "%Y-%m-%dT%H:%M:%S",
                                                    )
                                                    .replace(tzinfo=timezone.utc)
                                                    .astimezone(tz=None)
                                                    .timestamp()
                                                )
                                                if title is None or briefing is None or desc is None or exp is None:
                                                    break
                                                for tag in tags:
                                                    title = title.replace(tag, "**")
                                                    briefing = briefing.replace(tag, "**")
                                                    desc = desc.replace(tag, "**")
                                                if aj["reward"]["type"] == 1:
                                                    reward = aj["reward"]["amount"]
                                                else:
                                                    owner = await self.bot.fetch_user(self.owner_id)
                                                    await owner.send(f"Unknown reward type {str(aj['reward']['type'])}")
                                                    return
                                                morder = discord.File(
                                                    f"{self.here}\\images\\MajorOrder.png",
                                                    filename="mologo.png",
                                                )
                                                micon = discord.File(
                                                    f"{self.here}\\images\\Medal.png",
                                                    filename="medal.png",
                                                )
                                                emb = await aembed(
                                                    title,
                                                    briefing,
                                                    desc,
                                                    objectives,
                                                    reward,
                                                    exp,
                                                )
                                                msg = await channel.send(files=[morder, micon], embed=emb)
                                                for pin in await channel.pins():
                                                    await pin.unpin()
                                                await msg.pin()
                                                data["assign_id"] = aj["id"]
                                                f.seek(0)
                                                json.dump(data, f, indent=4)
                                                f.truncate()
                                                break
                                        else:
                                            aerror = True
                                            await asyncio.sleep(15)
                                            continue
                                    except json.JSONDecodeError:
                                        await asyncio.sleep(15)
                                        continue
                            except Exception:
                                owner = await self.bot.fetch_user(self.owner_id)
                                await owner.send("Error logged in HD2.")
                                ErrorLogger.run(traceback.format_exc())
                                break
                        if aerror is True and aerror is not None:
                            owner = await self.bot.fetch_user(self.owner_id)
                            await owner.send(f"aresponse status code {aresponse.status}")
                    await asyncio.sleep(0)
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

    @hd2.command(
        name="warstatus",
        description="Get current Galactic War status for Helldivers 2.",
    )
    @app_commands.checks.cooldown(1, 30, key=lambda i: (i.guild_id))
    async def warstatus(self, interaction: discord.Interaction, planet: str | None):
        try:

            async def embed(
                name: str,
                owner: str,
                liberation: str,
                players: str,
                major: bool,
                time: str,
                attacker: str,
                color: discord.Color,
                biome: dict,
                hazards: dict,
                event: bool,
            ):
                embed = discord.Embed(color=color)
                embed.title = name
                embed.description = f"{owner} control"
                if owner == "Super Earth":
                    if event is not None:
                        embed.add_field(name="Attacker:", value=attacker)
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
                embed.add_field(
                    name="Biome:",
                    value=f"__{biome['name']}__\n{biome['description']}",
                    inline=False,
                )
                h1 = []
                for hazard in hazards:
                    hz = f"__{hazard['name']}__\n{hazard['description']}"
                    h1.append(hz)
                h2 = "\n".join(h1)
                embed.add_field(name="Hazards:", value=h2, inline=False)
                embed.set_footer(text=f"{players} Helldivers", icon_url="attachment://hdlogo.png")
                if major is True:
                    embed.set_author(name="MAJOR ORDER", icon_url="attachment://mologo.png")
                embed.timestamp = datetime.now()
                return embed

            await interaction.response.defer()
            if planet is not None:
                async with ClientSession(headers=self.headers) as session:
                    for i in range(3):  # single planet
                        async with session.get(f"{self.api}/planets") as p1response:
                            if p1response.status == 200:
                                p1error = False
                                p1j = await p1response.json()
                                if p1j == []:
                                    await interaction.followup.send("p1response returned empty")
                                    return
                                for p in p1j:
                                    if planet.lower() == p["name"].lower():
                                        files = set()
                                        if p["currentOwner"] == "Humans":
                                            owner = "Super Earth"
                                            selogo = discord.File(
                                                f"{self.here}\\images\\SuperEarth.png",
                                                filename="selogo.png",
                                            )
                                            files.add(selogo)
                                            color = 0xB5D9E9
                                            if p["event"] is not None:
                                                event = True
                                                end = (
                                                    datetime.strptime(
                                                        p["event"]["endTime"][:19].strip(),
                                                        "%Y-%m-%dT%H:%M:%S",
                                                    )
                                                    .replace(tzinfo=timezone.utc)
                                                    .astimezone(tz=None)
                                                )
                                                now = datetime.now(UTC)
                                                rdelta = relativedelta(end, now)
                                                time = f"{rdelta.days}D:{rdelta.hours}H:{rdelta.minutes}M:{rdelta.seconds}S"
                                                attacker = p["event"]["faction"].replace("Automaton", "Automatons")
                                                lib = str(
                                                    round(
                                                        float(
                                                            (p["event"]["maxHealth"] - p["event"]["health"])
                                                            / (p["event"]["maxHealth"])
                                                            * 100
                                                        ),
                                                        5,
                                                    )
                                                )
                                            else:
                                                event = None
                                                end = None
                                                lib = None
                                                attacker = None
                                                time = None
                                        else:
                                            if p["currentOwner"] == "Terminids":
                                                owner = "Terminid"
                                                tlogo = discord.File(
                                                    f"{self.here}\\images\\Terminid.png",
                                                    filename="tlogo.png",
                                                )
                                                files.add(tlogo)
                                                color = 0xFFB800
                                            elif p["currentOwner"] == "Automaton":
                                                owner = p["currentOwner"]
                                                alogo = discord.File(
                                                    f"{self.here}\\images\\Automaton.png",
                                                    filename="alogo.png",
                                                )
                                                files.add(alogo)
                                                color = 0xFF6161
                                            elif p["currentOwner"] == "Illuminate":
                                                owner = p["currentOwner"]
                                                ilogo = discord.File(
                                                    f"{self.here}\\images\\Illuminate.png",
                                                    filename="ilogo.png",
                                                )
                                                files.add(ilogo)
                                                color = 0x000000
                                            lib = str(
                                                round(
                                                    float((p["maxHealth"] - p["health"]) / (p["maxHealth"]) * 100),
                                                    5,
                                                )
                                            )
                                            time = None
                                            attacker = None
                                            event = None
                                        hdlogo = discord.File(
                                            f"{self.here}\\images\\Helldivers.png",
                                            filename="hdlogo.png",
                                        )
                                        files.add(hdlogo)
                                        emb = await embed(
                                            p["name"],
                                            owner,
                                            lib,
                                            p["statistics"]["playerCount"],
                                            None,
                                            time,
                                            attacker,
                                            color,
                                            p["biome"],
                                            p["hazards"],
                                            event,
                                        )
                                        await interaction.followup.send(files=files, embed=emb)
                                        await asyncio.sleep(0)
                                        return
                                    else:
                                        continue
                                await interaction.followup.send("Planet not found. Double check spelling.")
                                await asyncio.sleep(0)
                                return
                            else:
                                p1error = True
                                await asyncio.sleep(15)
                                continue
                    if p1error is True and p1error is not None:
                        await interaction.followup.send(
                            f"aresponse status code {p1response.status}. Failed after 3 tries."
                        )
                        return
            async with ClientSession(headers=self.headers) as session:
                for i in range(3):  # cresponse
                    async with session.get(f"{self.api}/campaigns") as cresponse:
                        if cresponse.status == 200:
                            cerror = False
                            cj = await cresponse.json()
                            if cj == []:
                                await interaction.followup.send("cresponse returned empty.")
                                return
                            planets = []
                            aplanetdata = {}
                            tplanetdata = {}
                            iplanetdata = {}
                            seplanetdata = {}
                            for c in cj:
                                planets.append(c["planet"])
                            for planet in planets:  # build planet lists
                                index = planet["index"]
                                name = planet["name"]

                                owner = planet["currentOwner"]
                                players = planet["statistics"]["playerCount"]
                                biome = planet["biome"]
                                hazards = planet["hazards"]
                                if owner == "Humans":
                                    end = (
                                        datetime.strptime(
                                            planet["event"]["endTime"][:19].strip(),
                                            "%Y-%m-%dT%H:%M:%S",
                                        )
                                        .replace(tzinfo=timezone.utc)
                                        .astimezone(tz=None)
                                    )
                                    attacker = planet["event"]["faction"].replace("Automaton", "Automatons")
                                    lib = str(
                                        round(
                                            float(
                                                (planet["event"]["maxHealth"] - planet["event"]["health"])
                                                / (planet["event"]["maxHealth"])
                                                * 100
                                            ),
                                            5,
                                        )
                                    )
                                    seplanetdata.update(
                                        {
                                            name: {
                                                "index": index,
                                                "lib": lib,
                                                "owner": owner,
                                                "end": end,
                                                "attacker": attacker,
                                                "players": players,
                                                "biome": biome,
                                                "hazards": hazards,
                                            }
                                        }
                                    )
                                else:
                                    lib = str(
                                        round(
                                            float(
                                                (planet["maxHealth"] - planet["health"]) / (planet["maxHealth"]) * 100
                                            ),
                                            5,
                                        )
                                    )
                                    if owner == "Automaton":
                                        aplanetdata.update(
                                            {
                                                name: {
                                                    "index": index,
                                                    "lib": lib,
                                                    "owner": owner,
                                                    "players": players,
                                                    "biome": biome,
                                                    "hazards": hazards,
                                                }
                                            }
                                        )
                                    elif owner == "Terminids":
                                        tplanetdata.update(
                                            {
                                                name: {
                                                    "index": index,
                                                    "lib": lib,
                                                    "owner": owner,
                                                    "players": players,
                                                    "biome": biome,
                                                    "hazards": hazards,
                                                }
                                            }
                                        )
                                    elif owner == "Illuminate":
                                        iplanetdata.update(
                                            {
                                                name: {
                                                    "index": index,
                                                    "lib": lib,
                                                    "owner": owner,
                                                    "players": players,
                                                    "biome": biome,
                                                    "hazards": hazards,
                                                }
                                            }
                                        )
                            for i in range(3):  # a2response
                                async with session.get(f"{self.api}/assignments") as a2response:
                                    if a2response.status == 200:
                                        a2error = False
                                        a2j = await a2response.json()
                                        mo = []
                                        if a2j == []:
                                            break
                                        else:
                                            for t in a2j[0]["tasks"]:
                                                mo.append(t["values"][2])
                                        break
                                    else:
                                        a2error = True
                                        await asyncio.sleep(15)
                                        continue
                            if a2error is True and a2error is not None:
                                await interaction.followup.send(
                                    f"aresponse status code {a2response.status}. Failed after 3 tries."
                                )
                                return

                            if not aplanetdata == {}:
                                aembl = []
                                afiles = set()
                                morder = None
                                hdlogo = discord.File(
                                    f"{self.here}\\images\\Helldivers.png",
                                    filename="hdlogo.png",
                                )
                                afiles.add(hdlogo)
                                alogo = discord.File(
                                    f"{self.here}\\images\\Automaton.png",
                                    filename="alogo.png",
                                )
                                afiles.add(alogo)
                                for planet in aplanetdata:
                                    if aplanetdata[planet]["index"] in mo:
                                        major = True
                                        if morder is None:
                                            morder = discord.File(
                                                f"{self.here}\\images\\MajorOrder.png",
                                                filename="mologo.png",
                                            )
                                            afiles.add(morder)
                                    else:
                                        major = False
                                    emb = await embed(
                                        planet,
                                        "Automaton",
                                        aplanetdata[planet]["lib"],
                                        aplanetdata[planet]["players"],
                                        major,
                                        None,
                                        None,
                                        0xFF6161,
                                        aplanetdata[planet]["biome"],
                                        aplanetdata[planet]["hazards"],
                                        None,
                                    )
                                    aembl.append(emb)
                                await interaction.followup.send(files=afiles, embeds=aembl)
                            if not tplanetdata == {}:
                                tembl = []
                                tfiles = set()
                                morder = None
                                hdlogo = discord.File(
                                    f"{self.here}\\images\\Helldivers.png",
                                    filename="hdlogo.png",
                                )
                                tfiles.add(hdlogo)
                                tlogo = discord.File(
                                    f"{self.here}\\images\\Terminid.png",
                                    filename="tlogo.png",
                                )
                                tfiles.add(tlogo)
                                for planet in tplanetdata:
                                    if tplanetdata[planet]["index"] in mo:
                                        major = True
                                        if morder is None:
                                            morder = discord.File(
                                                f"{self.here}\\images\\MajorOrder.png",
                                                filename="mologo.png",
                                            )
                                            tfiles.add(morder)
                                    else:
                                        major = False
                                    emb = await embed(
                                        planet,
                                        "Terminid",
                                        tplanetdata[planet]["lib"],
                                        tplanetdata[planet]["players"],
                                        major,
                                        None,
                                        None,
                                        0xFFB800,
                                        tplanetdata[planet]["biome"],
                                        tplanetdata[planet]["hazards"],
                                        None,
                                    )
                                    tembl.append(emb)
                                await interaction.followup.send(files=tfiles, embeds=tembl)
                            if not iplanetdata == {}:
                                iembl = []
                                ifiles = set()
                                morder = None
                                hdlogo = discord.File(
                                    f"{self.here}\\images\\Helldivers.png",
                                    filename="hdlogo.png",
                                )
                                ifiles.add(hdlogo)
                                ilogo = discord.File(
                                    f"{self.here}\\images\\Illuminate.png",
                                    filename="ilogo.png",
                                )
                                ifiles.add(ilogo)
                                for planet in iplanetdata:
                                    if iplanetdata[planet]["index"] in mo:
                                        major = True
                                        if morder is None:
                                            morder = discord.File(
                                                f"{self.here}\\images\\MajorOrder.png",
                                                filename="mologo.png",
                                            )
                                            ifiles.add(morder)
                                    else:
                                        major = False
                                    emb = await embed(
                                        planet,
                                        "Illuminate",
                                        iplanetdata[planet]["lib"],
                                        iplanetdata[planet]["players"],
                                        major,
                                        None,
                                        None,
                                        0x000000,
                                        iplanetdata[planet]["biome"],
                                        iplanetdata[planet]["hazards"],
                                        None,
                                    )
                                    iembl.append(emb)
                                await interaction.followup.send(files=ifiles, embeds=iembl)
                            if not seplanetdata == {}:
                                seembl = []
                                sefiles = set()
                                morder = None
                                hdlogo = discord.File(
                                    f"{self.here}\\images\\Helldivers.png",
                                    filename="hdlogo.png",
                                )
                                sefiles.add(hdlogo)
                                selogo = discord.File(
                                    f"{self.here}\\images\\SuperEarth.png",
                                    filename="selogo.png",
                                )
                                sefiles.add(selogo)
                                for planet in seplanetdata:
                                    if seplanetdata[planet]["index"] in mo:
                                        major = True
                                        if morder is None:
                                            morder = discord.File(
                                                f"{self.here}\\images\\MajorOrder.png",
                                                filename="mologo.png",
                                            )
                                            sefiles.add(morder)
                                    else:
                                        major = False
                                    now = datetime.now(UTC)
                                    rdelta = relativedelta(seplanetdata[planet]["end"], now)
                                    time = f"{rdelta.days}D:{rdelta.hours}H:{rdelta.minutes}M:{rdelta.seconds}S"
                                    emb = await embed(
                                        planet,
                                        "Super Earth",
                                        seplanetdata[planet]["lib"],
                                        seplanetdata[planet]["players"],
                                        major,
                                        time,
                                        seplanetdata[planet]["attacker"],
                                        0xB5D9E9,
                                        seplanetdata[planet]["biome"],
                                        seplanetdata[planet]["hazards"],
                                        True,
                                    )
                                    seembl.append(emb)
                                await interaction.followup.send(files=sefiles, embeds=seembl)

                        else:
                            cerror = True
                            await asyncio.sleep(15)
                            continue
                        break
                if cerror is True and cerror is not None:
                    await interaction.followup.send(f"cresponse status code {cresponse.status}. Failed after 3 tries.")
                    return
            await asyncio.sleep(0)
        except Exception:
            await interaction.followup.send("Error logged in HD2.")
            ErrorLogger.run(traceback.format_exc())
            await asyncio.sleep(0)

    @warstatus.autocomplete("planet")
    async def warstatus_autocomplete(
        self, interaction: discord.Interaction, current: str
    ) -> typing.List[app_commands.Choice[str]]:
        choices = []
        with open(f"{self.here}\\planets.json", "r", encoding="utf-8") as p:
            data = json.load(p)
            planets = data[current.strip()[0].upper()]
            for planet in planets:
                if current.strip().lower() in planet.lower():
                    choices.append(app_commands.Choice(name=planet, value=planet))
        return choices

    @warstatus.error
    async def warstatus_error(self, interaction: discord.Interaction, error):
        if isinstance(error, commands.CommandOnCooldown):
            await interaction.response.send(
                f"Command on cooldown, try again in {error.retry_after: .0f} seconds.",
                ephemeral=True,
            )

    @hd2.command(name="mostatus", description="Get current Major Order status for Helldivers 2.")
    @app_commands.checks.cooldown(1, 30, key=lambda i: (i.guild_id))
    async def mostatus(self, interaction: discord.Interaction):
        try:

            async def embed(
                title: str,
                briefing: str,
                description: str,
                objectives: list,
                reward: str,
                expire: int,
            ):
                try:
                    objective = "\n".join(objectives)
                    embed = discord.Embed(color=0xB5D9E9)
                    embed.title = title
                    embed.description = briefing
                    embed.add_field(name=description, value=objective)
                    embed.add_field(name="Expires:", value=f"<t:{expire}:R>", inline=False)
                    embed.set_thumbnail(url="attachment://mologo.png")
                    embed.set_footer(
                        text=f"REWARD: {reward} MEDALS",  # Reward type 1 is medals, maybe more rewards types in the future?
                        icon_url="attachment://medal.png",
                    )
                    embed.timestamp = datetime.now()
                    return embed
                except Exception:
                    await interaction.followup.send("Error logged in HD2.")
                    ErrorLogger.run(traceback.format_exc())

            await interaction.response.defer()
            async with ClientSession(headers=self.headers) as session:
                tags = ["<i=1>", "<i=3>", "</i>"]
                for i in range(3):
                    try:
                        async with session.get(f"{self.api}/assignments") as aresponse:
                            try:
                                aj = await aresponse.json()
                                objectives = []
                                if aresponse.status == 200:
                                    aerror = False
                                    if aj == []:
                                        await interaction.followup.send("Major Order not found.")
                                        return
                                    aj = aj[0]
                                    task = aj["tasks"][0]
                                    if task["type"] == 3:  # elimination
                                        prog = aj["progress"][0]
                                        goal = task["values"][2]
                                        objectives.append(
                                            f"{prog:,}/{goal:,} - {str(round(float((prog/goal)*100),1))}%"
                                        )
                                    elif task["type"] == 12:  # defend X planets
                                        prog = aj["progress"][0]
                                        goal = task["values"][0]
                                        objectives.append(f"{prog}/{goal} - {str(round(float((prog/goal)*100),1))}%")
                                    elif task["type"] == 11:  # liberation
                                        pindex = []
                                        prog = aj["progress"]
                                        for t in aj["tasks"]:
                                            pindex.append(t["values"][2])
                                        async with session.get(f"{self.api}/planets") as presponse:
                                            if presponse.status == 200:
                                                perror = False
                                                pj = await presponse.json()
                                                for i, j in enumerate(pindex):
                                                    for p in pj:
                                                        if p["index"] == j:
                                                            if prog[i] == 0:
                                                                lib = str(
                                                                    round(
                                                                        float(
                                                                            (p["maxHealth"] - p["health"])
                                                                            / (p["maxHealth"])
                                                                            * 100
                                                                        ),
                                                                        5,
                                                                    )
                                                                )
                                                                name = f"-{p['name']} | {lib}%"
                                                            elif prog[i] == 1:
                                                                name = f"~~-{p['name']}~~"
                                                            objectives.append(name)
                                            else:
                                                perror = True
                                                await asyncio.sleep(15)
                                                continue
                                        if perror is True and perror is not None:
                                            await interaction.followup.send(f"presponse status code {presponse.status}")
                                    elif task["type"] == 13:  # hold planets
                                        pindex = []
                                        prog = aj["progress"]
                                        for t in aj["tasks"]:
                                            pindex.append(t["values"][2])
                                        async with session.get(f"{self.api}/planets") as presponse:
                                            if presponse.status == 200:
                                                perror = False
                                                pj = await presponse.json()
                                                for i, j in enumerate(pindex):
                                                    for p in pj:
                                                        if p["index"] == j:
                                                            if prog[i] == 0:
                                                                name = f"-{p['name']}"
                                                            elif prog[i] == 1:
                                                                name = f"-{p['name']} ✓"
                                                            objectives.append(name)
                                            else:
                                                perror = True
                                                await asyncio.sleep(15)
                                                continue
                                        if perror is True and perror is not None:
                                            await interaction.followup.send(f"presponse status code {presponse.status}")
                                    else:
                                        await interaction.followup.send(
                                            f"Unknown task type {str(task['type'])}. Aborting..."
                                        )
                                        return
                                    title = aj["title"]
                                    briefing = aj["briefing"]
                                    desc = aj["description"]
                                    exp = round(
                                        datetime.strptime(
                                            aj["expiration"][:19].strip(),
                                            "%Y-%m-%dT%H:%M:%S",
                                        )
                                        .replace(tzinfo=timezone.utc)
                                        .astimezone(tz=None)
                                        .timestamp()
                                    )
                                    for tag in tags:
                                        title = title.replace(tag, "**")
                                        briefing = briefing.replace(tag, "**")
                                        desc = desc.replace(tag, "**")
                                    if aj["reward"]["type"] == 1:
                                        reward = aj["reward"]["amount"]
                                    else:
                                        await interaction.followup.send(
                                            f"Unknown reward type {str(aj['reward']['type'])}"
                                        )
                                        return
                                    morder = discord.File(
                                        f"{self.here}\\images\\MajorOrder.png",
                                        filename="mologo.png",
                                    )
                                    micon = discord.File(
                                        f"{self.here}\\images\\Medal.png",
                                        filename="medal.png",
                                    )
                                    emb = await embed(title, briefing, desc, objectives, reward, exp)
                                    await interaction.followup.send(files=[morder, micon], embed=emb)
                                    break
                                else:
                                    aerror = True
                                    await asyncio.sleep(15)
                                    continue
                            except json.JSONDecodeError:
                                await asyncio.sleep(15)
                                continue
                    except Exception:
                        await interaction.followup.send("Error logged in HD2.")
                        ErrorLogger.run(traceback.format_exc())
                        break
                if aerror is True and aerror is not None:
                    await interaction.followup.send(f"aresponse status code {aresponse.status}")
            await asyncio.sleep(0)
        except Exception:
            await interaction.followup.send("Error logged in HD2.")
            ErrorLogger.run(traceback.format_exc())

    @mostatus.error
    async def mostatus_error(self, interaction: discord.Interaction, error):
        if isinstance(error, commands.CommandOnCooldown):
            await interaction.response.send(
                f"Command on cooldown, try again in {error.retry_after: .0f} seconds.",
                ephemeral=True,
            )
