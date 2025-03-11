import asyncio
from contextlib import suppress
from datetime import datetime, UTC, timezone
import json
import math
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
        self.planet_tasks = [11, 12, 13]
        self.colors = {"SE": 0xB5D9E9, "DP": 0x2E3C4B, "AT": 0xFF6161, "TR": 0xFFB800, "IL": 0x9729FF}

        self.retry = 15
        self.update_cooldown = 1800

    hd2 = app_commands.Group(name="hd2", description="...")

    async def plural(self, num: int):
        return 0 if num == 1 else 1

    async def update(self):
        async def dembed(message: str, timestamp: datetime):
            try:
                embed = discord.Embed(color=self.colors["DP"])
                embed.description = message
                embed.timestamp = timestamp
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
            # reward: str,
            expire: int,
        ):
            try:
                objective = "\n".join(objectives)
                embed = discord.Embed(color=self.colors["SE"])
                embed.title = title
                embed.description = briefing
                embed.add_field(name=description, value=objective)
                embed.add_field(name="Expires:", value=f"<t:{expire}:R>", inline=False)
                embed.set_thumbnail(url="attachment://mologo.png")
                # embed.set_footer(
                #     text=f"REWARD: {reward} MEDALS",
                #     icon_url="attachment://medal.png",
                # )
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
                                                    ts = (
                                                        datetime.strptime(
                                                            d["published"][:19].strip(), "%Y-%m-%dT%H:%M:%S"
                                                        )
                                                        .replace(tzinfo=timezone.utc)
                                                        .astimezone(tz=None)
                                                    )
                                                    emb = await dembed(message=msg, timestamp=ts)
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
                        if derror is True and derror is not None and dresponse.status != 503:
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
                                            tasks = aj["tasks"]
                                            if aj["id"] != data["assign_id"]:
                                                pindex = []
                                                atype = {}
                                                acount = 0
                                                for task in tasks:
                                                    match task["type"]:
                                                        case 2:
                                                            if (
                                                                task["valueTypes"][4] == 5
                                                                and task["valueTypes"][4] != 0
                                                            ):
                                                                for sample in data["sample_ids"]:
                                                                    if task["values"][4] == sample["id"]:
                                                                        samples = sample["sample"]
                                                            else:
                                                                sample = "Unknown Samples"
                                                            if (
                                                                task["valueTypes"][8] == 12
                                                                and task["valueTypes"][8] != 0
                                                            ):
                                                                async with session.get(
                                                                    f"{self.api}/planets/{task['values'][8]}"
                                                                ) as psresponse:
                                                                    psj = await psresponse.json()
                                                                    if psresponse.status == 200:
                                                                        pname = f" on {psj['name']}"
                                                            else:
                                                                pname = ""
                                                            objectives.append(
                                                                f"-Collect {samples}{pname} | {task['values'][2]:,}"
                                                            )
                                                        case 3:
                                                            if task["valueTypes"][3] == 4 and task["values"][3] != 0:
                                                                for target in data["target_ids"]:
                                                                    if task["values"][3] == target["id"]:
                                                                        target = target["target"]
                                                                        break
                                                                    else:
                                                                        match task["values"][0]:
                                                                            case 2:
                                                                                target = "Unknown Terminids"
                                                                            case 3:
                                                                                target = "Unknown Automatons"
                                                                            case 4:
                                                                                target = "Unknown Illuminate"
                                                                            case _:
                                                                                target = "Enemies"
                                                            else:
                                                                match task["values"][0]:
                                                                    case 2:
                                                                        target = "Terminids"
                                                                    case 3:
                                                                        target = "Automatons"
                                                                    case 4:
                                                                        target = "Illuminate"
                                                                    case _:
                                                                        target = "Enemies"
                                                            if task["valueTypes"][5] == 5 and task["values"][5] != 0:
                                                                for weapon in data["weapon_ids"]:
                                                                    if task["values"][5] == weapon["id"]:
                                                                        t2 = f"with the {weapon['weapon']}"
                                                                        break
                                                                    else:
                                                                        t2 = "with a specific weapon"
                                                                target = f"{target} {t2}"
                                                            objectives.append(
                                                                f"-Eradicate {target} | {task['values'][2]:,}"
                                                            )
                                                        case 11:
                                                            pindex.append(task["values"][2])
                                                            atype[acount] = 11
                                                            acount += 1
                                                        case 12:
                                                            if task["values"][1] != 0:
                                                                match task["values"][1]:
                                                                    case 2:
                                                                        faction = "Terminid"
                                                                    case 3:
                                                                        faction = "Automaton"
                                                                    case 4:
                                                                        faction = "Illuminate"
                                                                    case _:
                                                                        faction = "[Unknown]"
                                                                attack = f" from {faction} attack"
                                                            else:
                                                                attack = ""
                                                            if task["values"][3] != 0:
                                                                async with session.get(
                                                                    f"{self.api}/planets/{task['values'][3]}"
                                                                ) as piresponse:
                                                                    pij = await piresponse.json()
                                                                    if piresponse.status == 200:
                                                                        pname = pij["name"]
                                                                    else:
                                                                        objectives.append(
                                                                            f"-Defend Planet | {str(task['values'][0])}"
                                                                        )
                                                                objectives.append(
                                                                    f"-Defend {pname} from {task['values'][0]} {['attack', 'attacks'][await self.plural(task['values'][0])]}"
                                                                )
                                                            objectives.append(
                                                                f"-Defend Planets{attack} | {str(task['values'][0])}"
                                                            )
                                                        case 13:
                                                            pindex.append(task["values"][2])
                                                            atype[acount] = 13
                                                            acount += 1
                                                        case 15:
                                                            objectives.append("-Capture more planets than the enemy.")
                                                        case _:
                                                            owner = await self.bot.fetch_user(self.owner_id)
                                                            await owner.send(
                                                                f"Unknown task type {str(task['type'])}. Aborting..."
                                                            )
                                                            ErrorLogger.run(str(aj))
                                                            return
                                                for i in range(3):
                                                    async with session.get(f"{self.api}/planets") as presponse:
                                                        if presponse.status == 200:
                                                            perror = False
                                                            pj = await presponse.json()
                                                            for i, j in enumerate(pindex):
                                                                for p in pj:
                                                                    if p["index"] == j:
                                                                        match atype[i]:
                                                                            case 11:
                                                                                objectives.append(
                                                                                    f"-Liberate {p['name']}"
                                                                                )
                                                                            case 13:
                                                                                objectives.append(f"-Hold {p['name']}")
                                                                            case _:
                                                                                objectives.append(f"-{p['name']}")
                                                            break
                                                        else:
                                                            perror = True
                                                            await asyncio.sleep(self.retry)
                                                            continue
                                                if perror is True and perror is not None:
                                                    owner = await self.bot.fetch_user(self.owner_id)
                                                    await owner.send(f"presponse status code {presponse.status}")
                                                    return
                                                title = aj["title"] if aj["title"] is not None else ""
                                                briefing = aj["briefing"] if aj["briefing"] is not None else ""
                                                desc = aj["description"] if aj["description"] is not None else ""
                                                exp = round(
                                                    datetime.strptime(
                                                        aj["expiration"][:19].strip(),
                                                        "%Y-%m-%dT%H:%M:%S",
                                                    )
                                                    .replace(tzinfo=timezone.utc)
                                                    .astimezone(tz=None)
                                                    .timestamp()
                                                )
                                                if any(field is None for field in [title, briefing, desc, exp]):
                                                    break
                                                for tag in tags:
                                                    title = title.replace(tag, "**")
                                                    briefing = briefing.replace(tag, "**")
                                                    desc = desc.replace(tag, "**")
                                                # if aj["reward"]["type"] == 1:
                                                #   reward = aj["reward"]["amount"]
                                                # this is not how rewards work
                                                # else:
                                                #     owner = await self.bot.fetch_user(self.owner_id)
                                                #     await owner.send(f"Unknown reward type {str(aj['reward']['type'])}")
                                                #     return
                                                morder = discord.File(
                                                    f"{self.here}\\images\\MajorOrder.png",
                                                    filename="mologo.png",
                                                )
                                                # micon = discord.File(
                                                #     f"{self.here}\\images\\Medal.png",
                                                #     filename="medal.png",
                                                # )
                                                emb = await aembed(
                                                    title,
                                                    briefing,
                                                    desc,
                                                    objectives,
                                                    # reward,
                                                    exp,
                                                )
                                                # msg = await channel.send(files=[morder, micon], embed=emb)
                                                msg = await channel.send(files=[morder], embed=emb)
                                                for pin in await channel.pins():
                                                    await pin.unpin()
                                                await msg.pin()
                                                data["assign_id"] = aj["id"]
                                                f.seek(0)
                                                json.dump(data, f, indent=4)
                                                f.truncate()
                                                break
                                            else:
                                                break
                                        else:
                                            aerror = True
                                            await asyncio.sleep(self.retry)
                                            continue
                                    except json.JSONDecodeError:
                                        await asyncio.sleep(self.retry)
                                        continue
                            except Exception:
                                owner = await self.bot.fetch_user(self.owner_id)
                                await owner.send("Error logged in HD2.")
                                ErrorLogger.run(traceback.format_exc())
                                break
                        if aerror is True and aerror is not None and aresponse.status != 503:
                            owner = await self.bot.fetch_user(self.owner_id)
                            await owner.send(f"aresponse status code {aresponse.status}")
                    await asyncio.sleep(0)
                await asyncio.sleep(self.update_cooldown)
            except ConnectionAbortedError:
                ErrorLogger.run(traceback.format_exc())
                await asyncio.sleep(self.update_cooldown)
                continue
            except Exception:
                owner = await self.bot.fetch_user(self.owner_id)
                await owner.send("Error logged in HD2.")
                ErrorLogger.run(traceback.format_exc())
                await asyncio.sleep(self.retry)
                continue

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.wait_until_ready()
        self.update_task = asyncio.create_task(self.update())
        await self.update_task

    async def cog_unload(self):
        self.update_task.cancel()

    @commands.command(hidden=True)
    @commands.is_owner()
    async def hd(self, ctx):
        self.update_task = asyncio.create_task(self.update())
        await self.update_task

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
                attorigin: str,
                color: discord.Color,
                biome: dict,
                hazards: dict,
                event: bool,
                regen: str,
            ):
                embed = discord.Embed(color=color)
                embed.title = name
                embed.description = f"{owner} control"
                bar1 = "█" * int((math.floor(float(liberation)) / 10))
                bar3 = "▁" * (10 - len(bar1) - 1)
                if owner == "Super Earth":
                    if event is not None:
                        embed.add_field(name="Attacker:", value=attacker)
                        embed.add_field(name="Attack Origin:", value=attorigin)
                        embed.add_field(name="Time Remaining:", value=time, inline=False)
                        embed.add_field(name="Defense:", value=f"{bar1}▒{bar3} │ {liberation}%")
                    embed.set_thumbnail(url="attachment://selogo.png")
                else:
                    embed.add_field(name="Liberation:", value=f"{bar1}▒{bar3} │ {liberation}%")
                    embed.add_field(name="Enemy Resistance:", value=f"{regen}%", inline=False)
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
                return embed

            await interaction.response.defer()
            if planet is not None:  # single planet
                async with ClientSession(headers=self.headers) as session:
                    for i in range(3):
                        async with session.get(f"{self.api}/planets") as p1response:
                            if p1response.status == 200:
                                p1error = False
                                p1j = await p1response.json()
                                if p1j == []:
                                    await interaction.followup.send("p1response returned empty")
                                    return
                                for p in p1j:
                                    if planet.lower() == p["name"].lower():
                                        for i in range(3):
                                            async with session.get(f"{self.api}/assignments") as a1response:
                                                if a1response.status == 200:
                                                    a1error = False
                                                    a1j = await a1response.json()
                                                    mo = []
                                                    if a1j == []:
                                                        await interaction.followup.send("a1response returned empty")
                                                        break
                                                    else:
                                                        for t in a1j[0]["tasks"]:
                                                            if t["type"] in self.planet_tasks:
                                                                mo.append(t["values"][2])
                                                            else:
                                                                continue
                                                    break
                                                else:
                                                    a1error = True
                                                    await asyncio.sleep(self.retry)
                                                    continue
                                        if a1error is True and a1error is not None:
                                            await interaction.followup.send(
                                                f"a1response status code {a1response.status}. Failed after 3 tries."
                                            )
                                            return
                                        files = set()
                                        if p["index"] in mo:
                                            major = True
                                            morder = discord.File(
                                                f"{self.here}\\images\\MajorOrder.png", filename="mologo.png"
                                            )
                                            files.add(morder)
                                        else:
                                            major = False
                                        if p["currentOwner"] == "Humans":
                                            owner = "Super Earth"
                                            selogo = discord.File(
                                                f"{self.here}\\images\\SuperEarth.png",
                                                filename="selogo.png",
                                            )
                                            files.add(selogo)
                                            color = self.colors["SE"]
                                            regen = None
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
                                                if not p["attacking"]:
                                                    attorigin = "Unknown"
                                                else:
                                                    for p2 in p1j:
                                                        if p2["index"] == p["attacking"][0]:
                                                            attorigin = p2["name"]
                                                            break
                                                        else:
                                                            attorigin = "Unknown"
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
                                                attorigin = None
                                                time = None
                                        else:
                                            match p["currentOwner"]:
                                                case "Terminids":
                                                    owner = "Terminid"
                                                    tlogo = discord.File(
                                                        f"{self.here}\\images\\Terminid.png",
                                                        filename="tlogo.png",
                                                    )
                                                    files.add(tlogo)
                                                    color = self.colors["TR"]
                                                case "Automaton":
                                                    owner = p["currentOwner"]
                                                    alogo = discord.File(
                                                        f"{self.here}\\images\\Automaton.png",
                                                        filename="alogo.png",
                                                    )
                                                    files.add(alogo)
                                                    color = self.colors["AT"]
                                                case "Illuminate":
                                                    owner = p["currentOwner"]
                                                    ilogo = discord.File(
                                                        f"{self.here}\\images\\Illuminate.png",
                                                        filename="ilogo.png",
                                                    )
                                                    files.add(ilogo)
                                                    color = self.colors["IL"]
                                            lib = str(
                                                round(
                                                    float((p["maxHealth"] - p["health"]) / (p["maxHealth"]) * 100),
                                                    5,
                                                )
                                            )
                                            regen = str(
                                                round(
                                                    round(
                                                        float(((p["regenPerSecond"] * 3600) / p["maxHealth"]) * 100), 1
                                                    )
                                                    * 2
                                                )
                                                / 2
                                            )
                                            time = None
                                            attacker = None
                                            attorigin = None
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
                                            major,
                                            time,
                                            attacker,
                                            attorigin,
                                            color,
                                            p["biome"],
                                            p["hazards"],
                                            event,
                                            regen,
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
                                await asyncio.sleep(self.retry)
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
                                    if not planet["attacking"]:
                                        attorigin = "Unknown"
                                    else:
                                        for p in planets:
                                            if p["index"] == planet["attacking"][0]:
                                                attorigin = p["name"]
                                                break
                                            else:
                                                attorigin = "Unknown"
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
                                                "attorigin": attorigin,
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
                                    regen = str(
                                        round(
                                            round(
                                                float(((planet["regenPerSecond"] * 3600) / planet["maxHealth"]) * 100),
                                                1,
                                            )
                                            * 2
                                        )
                                        / 2
                                    )
                                    match owner:
                                        case "Automaton":
                                            aplanetdata.update(
                                                {
                                                    name: {
                                                        "index": index,
                                                        "lib": lib,
                                                        "owner": owner,
                                                        "players": players,
                                                        "biome": biome,
                                                        "hazards": hazards,
                                                        "regen": regen,
                                                    }
                                                }
                                            )
                                        case "Terminids":
                                            tplanetdata.update(
                                                {
                                                    name: {
                                                        "index": index,
                                                        "lib": lib,
                                                        "owner": owner,
                                                        "players": players,
                                                        "biome": biome,
                                                        "hazards": hazards,
                                                        "regen": regen,
                                                    }
                                                }
                                            )
                                        case "Illuminate":
                                            iplanetdata.update(
                                                {
                                                    name: {
                                                        "index": index,
                                                        "lib": lib,
                                                        "owner": owner,
                                                        "players": players,
                                                        "biome": biome,
                                                        "hazards": hazards,
                                                        "regen": regen,
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
                                                if t["type"] in self.planet_tasks:
                                                    mo.append(t["values"][2])
                                                else:
                                                    continue
                                        break
                                    else:
                                        a2error = True
                                        await asyncio.sleep(self.retry)
                                        continue
                            if a2error is True and a2error is not None:
                                await interaction.followup.send(
                                    f"a2response status code {a2response.status}. Failed after 3 tries."
                                )
                                return

                            if not aplanetdata == {}:
                                aembl = []
                                aembl2 = []
                                for planet in aplanetdata:
                                    if aplanetdata[planet]["index"] in mo:
                                        major = True
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
                                        None,
                                        self.colors["AT"],
                                        aplanetdata[planet]["biome"],
                                        aplanetdata[planet]["hazards"],
                                        None,
                                        aplanetdata[planet]["regen"],
                                    )
                                    if len(aembl) < 10:
                                        aembl.append(emb)
                                    else:
                                        aembl2.append(emb)
                                    aembll = [aembl, aembl2]
                                for elist in aembll:
                                    if elist:
                                        morder = None
                                        afiles = set()
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
                                        for e in elist:
                                            if e.author and morder is None:
                                                morder = discord.File(
                                                    f"{self.here}\\images\\MajorOrder.png",
                                                    filename="mologo.png",
                                                )
                                                afiles.add(morder)
                                                break
                                        await interaction.followup.send(files=afiles, embeds=elist)
                            if not tplanetdata == {}:
                                tembl = []
                                tembl2 = []
                                for planet in tplanetdata:
                                    if tplanetdata[planet]["index"] in mo:
                                        major = True
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
                                        None,
                                        self.colors["TR"],
                                        tplanetdata[planet]["biome"],
                                        tplanetdata[planet]["hazards"],
                                        None,
                                        tplanetdata[planet]["regen"],
                                    )
                                    if len(tembl) < 10:
                                        tembl.append(emb)
                                    else:
                                        tembl2.append(emb)
                                    tembll = [tembl, tembl2]
                                for elist in tembll:
                                    if elist:
                                        morder = None
                                        tfiles = set()
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
                                        for e in elist:
                                            if e.author and morder is None:
                                                morder = discord.File(
                                                    f"{self.here}\\images\\MajorOrder.png",
                                                    filename="mologo.png",
                                                )
                                                tfiles.add(morder)
                                                break
                                        await interaction.followup.send(files=tfiles, embeds=elist)
                            if not iplanetdata == {}:
                                iembl = []
                                iembl2 = []
                                for planet in iplanetdata:
                                    if iplanetdata[planet]["index"] in mo:
                                        major = True
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
                                        None,
                                        self.colors["IL"],
                                        iplanetdata[planet]["biome"],
                                        iplanetdata[planet]["hazards"],
                                        None,
                                        iplanetdata[planet]["regen"],
                                    )
                                    if len(iembl) < 10:
                                        iembl.append(emb)
                                    else:
                                        iembl2.append(emb)
                                    iembll = [iembl, iembl2]
                                for elist in iembll:
                                    if elist:
                                        morder = None
                                        ifiles = set()
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
                                        for e in elist:
                                            if e.author and morder is None:
                                                morder = discord.File(
                                                    f"{self.here}\\images\\MajorOrder.png",
                                                    filename="mologo.png",
                                                )
                                                tfiles.add(morder)
                                                break
                                        await interaction.followup.send(files=ifiles, embeds=elist)
                            if not seplanetdata == {}:
                                seembl = []
                                seembl2 = []
                                for planet in seplanetdata:
                                    if seplanetdata[planet]["index"] in mo:
                                        major = True
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
                                        seplanetdata[planet]["attorigin"],
                                        self.colors["SE"],
                                        seplanetdata[planet]["biome"],
                                        seplanetdata[planet]["hazards"],
                                        True,
                                        None,
                                    )
                                    if len(seembl) < 10:
                                        seembl.append(emb)
                                    else:
                                        seembl2.append(emb)
                                    seembll = [seembl, seembl2]
                                for elist in seembll:
                                    if elist:
                                        morder = None
                                        sefiles = set()
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
                                        for e in elist:
                                            if e.author and morder is None:
                                                morder = discord.File(
                                                    f"{self.here}\\images\\MajorOrder.png",
                                                    filename="mologo.png",
                                                )
                                                tfiles.add(morder)
                                                break
                                        await interaction.followup.send(files=sefiles, embeds=elist)

                        else:
                            cerror = True
                            await asyncio.sleep(self.retry)
                            continue
                        break
                if cerror is True and cerror is not None:
                    await interaction.followup.send(f"cresponse status code {cresponse.status}. Failed after 3 tries.")
                    return
            await asyncio.sleep(0)
        except ConnectionAbortedError:
            ErrorLogger.run(traceback.format_exc())
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
                # reward: str,
                expire: int,
            ):
                try:
                    objective = "\n".join(objectives)
                    embed = discord.Embed(color=self.colors["SE"])
                    embed.title = title
                    embed.description = briefing
                    embed.add_field(name=description, value=objective)
                    embed.add_field(name="Expires:", value=f"<t:{expire}:R>", inline=False)
                    embed.set_thumbnail(url="attachment://mologo.png")
                    # embed.set_footer(
                    #     text=f"REWARD: {reward} MEDALS",
                    #     icon_url="attachment://medal.png",
                    # )
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
                                    prog = aj["progress"]
                                    tasks = aj["tasks"]
                                    pindex = []
                                    atype = {}
                                    acount = 0
                                    index = 0
                                    for task in tasks:
                                        match task["type"]:
                                            case 2:  # collect
                                                if task["valueTypes"][4] == 5 and task["valueTypes"][4] != 0:
                                                    with open(self.file, "r", encoding="utf-8") as f:
                                                        data = json.load(f)
                                                        for sample in data["sample_ids"]:
                                                            if task["values"][4] == sample["id"]:
                                                                samples = sample["sample"]
                                                else:
                                                    sample = "Unknown Samples"
                                                if task["valueTypes"][8] == 12 and task["valueTypes"][8] != 0:
                                                    async with session.get(
                                                        f"{self.api}/planets/{task['values'][8]}"
                                                    ) as psresponse:
                                                        psj = await psresponse.json()
                                                        if psresponse.status == 200:
                                                            pname = f" on {psj['name']}"
                                                else:
                                                    pname = ""
                                                goal = task["values"][2]
                                                objectives.append(
                                                    f"-Collect {samples}{pname} | {prog[index]:,} / {goal} - {str(round(float((prog[index] / goal) * 100), 1))}%"
                                                )
                                            case 3:  # eradicate
                                                if task["valueTypes"][3] == 4 and task["values"][3] != 0:
                                                    with open(self.file, "r", encoding="utf-8") as f:
                                                        data = json.load(f)
                                                        for target in data["target_ids"]:
                                                            if task["values"][3] == target["id"]:
                                                                target = target["target"]
                                                                break
                                                            else:
                                                                match task["values"][0]:
                                                                    case 2:
                                                                        target = "Unknown Terminids"
                                                                    case 3:
                                                                        target = "Unknown Automatons"
                                                                    case 4:
                                                                        target = "Unknown Illuminate"
                                                                    case _:
                                                                        target = "Enemies"
                                                else:
                                                    match task["values"][0]:
                                                        case 2:
                                                            target = "Terminids"
                                                        case 3:
                                                            target = "Automatons"
                                                        case 4:
                                                            target = "Illuminate"
                                                        case _:
                                                            target = "Enemies"
                                                if task["valueTypes"][5] == 5 and task["values"][5] != 0:
                                                    with open(self.file, "r", encoding="utf-8") as f:
                                                        data = json.load(f)
                                                        for weapon in data["weapon_ids"]:
                                                            if task["values"][5] == weapon["id"]:
                                                                t2 = f"with the {weapon['weapon']}"
                                                                break
                                                            else:
                                                                t2 = "with a specific weapon"
                                                        target = f"{target} {t2}"
                                                goal = task["values"][2]
                                                objectives.append(
                                                    f"-Eradicate {target} | {prog[index]:,} / {goal:,} - {str(round(float((prog[index] / goal) * 100), 1))}%"
                                                )
                                            case 11:  # liberate
                                                pindex.append(task["values"][2])
                                                atype[acount] = 11
                                                acount += 1
                                            case 12:  # defend
                                                goal = task["values"][0]
                                                if task["values"][1] != 0:
                                                    match task["values"][1]:
                                                        case 2:
                                                            faction = "Terminid"
                                                        case 3:
                                                            faction = "Automaton"
                                                        case 4:
                                                            faction = "Illuminate"
                                                        case _:
                                                            faction = "[Unknown]"
                                                    attack = f" from {faction} attack"
                                                else:
                                                    attack = ""
                                                if task["values"][3] != 0:
                                                    async with session.get(
                                                        f"{self.api}/planets/{task['values'][3]}"
                                                    ) as piresponse:
                                                        pij = await piresponse.json()
                                                        if piresponse.status == 200:
                                                            pname = pij["name"]
                                                        else:
                                                            objectives.append(
                                                                f"-Defend Planet from {goal} {['attack', 'attacks'][await self.plural(goal)]} | {prog[index]} / {goal} - {str(round(float((prog[index] / goal) * 100), 1))}%"
                                                            )
                                                    objectives.append(
                                                        f"-Defend {pname} from {goal} {['attack', 'attacks'][await self.plural(goal)]} | {prog[index]} / {goal} - {str(round(float((prog[index] / goal) * 100), 1))}%"
                                                    )
                                                else:
                                                    objectives.append(
                                                        f"-Defend Planets{attack} | {prog[index]} / {goal} - {str(round(float((prog[index] / goal) * 100), 1))}%"
                                                    )
                                            case 13:  # control
                                                pindex.append(task["values"][2])
                                                atype[acount] = 13
                                                acount += 1
                                            case 15:
                                                bar1 = (
                                                    "▁" * (10 + prog[index]) + "█" * (prog[index] * -1)
                                                    if prog[index] < 0
                                                    else "▁" * 10
                                                )
                                                bar2 = (
                                                    "█" * prog[index] + "▁" * (10 - prog[index])
                                                    if prog[index] > 0
                                                    else "▁" * 10
                                                )
                                                objectives.append(
                                                    f"-Capture more planets than the enemy.\n\n{bar1}│{bar2}"
                                                )
                                            case _:
                                                await interaction.followup.send(
                                                    f"Unknown task type {str(task['type'])}. Aborting..."
                                                )
                                                ErrorLogger.run(str(aj))
                                                return
                                        index += 1
                                    if pindex:
                                        async with session.get(f"{self.api}/planets") as presponse:
                                            if presponse.status == 200:
                                                perror = False
                                                pj = await presponse.json()
                                                for i, j in enumerate(pindex):
                                                    for p in pj:
                                                        if p["index"] == j:
                                                            if prog[i] == 0 and p["currentOwner"] != "Humans":
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
                                                                name = f"{p['name']} | {lib}%"
                                                            else:
                                                                if p["event"] is not None:
                                                                    lib = str(
                                                                        round(
                                                                            float(
                                                                                (
                                                                                    p["event"]["maxHealth"]
                                                                                    - p["event"]["health"]
                                                                                )
                                                                                / (p["event"]["maxHealth"])
                                                                                * 100
                                                                            ),
                                                                            5,
                                                                        )
                                                                    )
                                                                    name = f"{p['name']} | ⚠ {lib}%"
                                                                else:
                                                                    name = f"{p['name']} | ✓"
                                                            match atype[i]:
                                                                case 11:
                                                                    objectives.append(f"-Liberate {name}")
                                                                case 13:
                                                                    objectives.append(f"-Hold {name}")
                                                                case _:
                                                                    objectives.append(name)
                                            else:
                                                perror = True
                                                await asyncio.sleep(self.retry)
                                                continue
                                        if perror is True and perror is not None:
                                            await interaction.followup.send(f"presponse status code {presponse.status}")
                                    title = aj["title"] if aj["title"] is not None else ""
                                    briefing = aj["briefing"] if aj["briefing"] is not None else ""
                                    desc = aj["description"] if aj["description"] is not None else ""
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
                                    # if aj["reward"]["type"] == 1:
                                    #     reward = aj["reward"]["amount"]
                                    # else:
                                    #     await interaction.followup.send(
                                    #         f"Unknown reward type {str(aj['reward']['type'])}"
                                    #     )
                                    #     return
                                    morder = discord.File(
                                        f"{self.here}\\images\\MajorOrder.png",
                                        filename="mologo.png",
                                    )
                                    # micon = discord.File(
                                    #     f"{self.here}\\images\\Medal.png",
                                    #     filename="medal.png",
                                    # )
                                    # emb = await embed(title, briefing, desc, objectives, reward, exp)
                                    emb = await embed(title, briefing, desc, objectives, exp)
                                    # await interaction.followup.send(files=[morder, micon], embed=emb)
                                    await interaction.followup.send(files=[morder], embed=emb)
                                    break
                                else:
                                    aerror = True
                                    await asyncio.sleep(self.retry)
                                    continue
                            except json.JSONDecodeError:
                                await asyncio.sleep(self.retry)
                                continue
                    except Exception:
                        await interaction.followup.send("Error logged in HD2.")
                        ErrorLogger.run(traceback.format_exc())
                        break
                if aerror is True and aerror is not None:
                    await interaction.followup.send(f"aresponse status code {aresponse.status}")
            await asyncio.sleep(0)
        except ConnectionAbortedError:
            ErrorLogger.run(traceback.format_exc())
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
