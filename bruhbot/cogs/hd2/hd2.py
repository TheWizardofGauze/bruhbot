import asyncio
from contextlib import suppress
from datetime import datetime, UTC, timezone
import json
import math
import os
import traceback
import typing

from aiohttp import ClientSession, client_exceptions
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
        self.channel_id = int(os.getenv("HD2_CID"))
        self.testing_id = int(os.getenv("HD2_TID"))
        self.planet_tasks = [11, 12, 13]
        self.colors = {"SE": 0xB5D9E9, "DP": 0x2E3C4B, "AT": 0xFF6161, "TR": 0xFFB800, "IL": 0xCE8AEA}
        self.images = {
            "MO": f"{self.here}\\images\\MajorOrder.png",
            "HD": f"{self.here}\\images\\Helldivers.png",
            "SE": f"{self.here}\\images\\SuperEarth.png",
            "TR": f"{self.here}\\images\\Terminid.png",
            "AT": f"{self.here}\\images\\Automaton.png",
            "IL": f"{self.here}\\images\\Illuminate.png",
        }
        self.retry = 15
        self.update_cooldown = 1800
        self.status_codes = [400, 401, 403, 404, 429]

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
                return embed
            except Exception:
                owner = await self.bot.fetch_user(self.owner_id)
                await owner.send("Error logged in HD2.")
                ErrorLogger.run(traceback.format_exc())

        tags = ["<i=1>", "<i=3>", "</i>", "</>"]
        while True:
            try:
                with open(self.file, "r+", encoding="utf-8") as f:
                    data = json.load(f)
                    channel = self.bot.get_channel(self.channel_id)
                    async with ClientSession(headers=self.headers) as session:
                        for i in range(3):  # dresponse
                            try:
                                async with session.get(f"{self.api}/dispatches") as dresponse:
                                    try:
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
                                                            datetime
                                                            .strptime(d["published"][:19].strip(), "%Y-%m-%dT%H:%M:%S")
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
                                    except (json.JSONDecodeError, client_exceptions.ClientPayloadError):
                                        await asyncio.sleep(self.retry)
                                        continue
                            except (ConnectionAbortedError, asyncio.TimeoutError):
                                ErrorLogger.run(traceback.format_exc())
                                continue
                            except Exception:
                                owner = await self.bot.fetch_user(self.owner_id)
                                await owner.send("Error logged in HD2.")
                                ErrorLogger.run(traceback.format_exc())
                                break
                        if derror is True and derror is not None and dresponse.status in self.status_codes:
                            owner = await self.bot.fetch_user(self.owner_id)
                            await owner.send(f"dresponse status code {dresponse.status}")
                    await asyncio.sleep(0)
                    async with ClientSession(headers=self.headers) as session:
                        for i in range(3):  # aresponse
                            try:
                                async with session.get(f"{self.api}/assignments") as aresponse:
                                    try:
                                        if aresponse.status == 200:
                                            aerror = False
                                            aj = await aresponse.json()
                                            if aj == []:
                                                ErrorLogger.run("aresponse returned empty.")
                                                break
                                            molist = []
                                            for mo in aj:
                                                objectives = []
                                                tasks = mo["tasks"]
                                                molist.append(mo["id"])
                                                if mo["id"] not in data["assign_ids"]:
                                                    pindex = []
                                                    atype = {}
                                                    acount = 0
                                                    for task in tasks:
                                                        match task["type"]:
                                                            case 2:  # collect
                                                                if (
                                                                    task["valueTypes"][4] == 5
                                                                    and task["values"][4] != 0
                                                                ):
                                                                    for sample in data["sample_ids"]:
                                                                        if task["values"][4] == sample["id"]:
                                                                            samples = f"**{sample['sample']}**"
                                                                else:
                                                                    sample = "Unknown Samples"
                                                                if (
                                                                    task["valueTypes"][8] == 12
                                                                    and task["values"][8] != 0
                                                                ):
                                                                    async with session.get(
                                                                        f"{self.api}/planets/{task['values'][8]}"
                                                                    ) as psresponse:
                                                                        psj = await psresponse.json()
                                                                        if psresponse.status == 200:
                                                                            pname = f" on **{psj['name']}**"
                                                                elif task["values"][8] == 0 and task["values"][0] != 0:
                                                                    match task["values"][0]:
                                                                        case 2:
                                                                            pname = " on Terminid controlled planets"
                                                                        case 3:
                                                                            pname = " on Automaton controlled planets"
                                                                        case 4:
                                                                            pname = " on Illuminate controlled planets"
                                                                        case _:
                                                                            pname = ""
                                                                else:
                                                                    pname = ""
                                                                objectives.append(
                                                                    f"- Collect {samples}{pname} | {task['values'][2]:,}"
                                                                )
                                                            case 3:  # eradicate
                                                                if (
                                                                    task["valueTypes"][3] == 4
                                                                    and task["values"][3] != 0
                                                                ):
                                                                    for target in data["target_ids"]:
                                                                        if task["values"][3] == target["id"]:
                                                                            target = f"**{target['target']}**"
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
                                                                            target = "**Terminids**"
                                                                        case 3:
                                                                            target = "**Automatons**"
                                                                        case 4:
                                                                            target = "**Illuminate**"
                                                                        case _:
                                                                            target = "Enemies"
                                                                if (
                                                                    task["valueTypes"][5] == 5
                                                                    and task["values"][5] != 0
                                                                ):
                                                                    for weapon in data["weapon_ids"]:
                                                                        if task["values"][5] == weapon["id"]:
                                                                            t2 = f"with the **{weapon['weapon']}**"
                                                                            break
                                                                        else:
                                                                            t2 = "with a specific weapon"
                                                                    target = f"{target} {t2}"
                                                                if (
                                                                    task["valueTypes"][9] == 12
                                                                    and task["values"][9] != 0
                                                                ):
                                                                    async with session.get(
                                                                        f"{self.api}/planets/{task['values'][9]}"
                                                                    ) as piresponse:
                                                                        pij = await piresponse.json()
                                                                        if piresponse.status == 200:
                                                                            pname = f" on **{pij['name']}**"
                                                                else:
                                                                    pname = ""
                                                                objectives.append(
                                                                    f"- Eradicate {target}{pname} | {task['values'][2]:,}"
                                                                )
                                                            case 7:  # extract
                                                                if task["values"][0] != 0:
                                                                    match task["values"][0]:
                                                                        case 2:
                                                                            faction = " against **Terminids**"
                                                                        case 3:
                                                                            faction = " against **Automatons**"
                                                                        case 4:
                                                                            faction = " against **Illuminate**"
                                                                        case _:
                                                                            faction = " against [Unknown]"
                                                                else:
                                                                    faction = ""
                                                                objectives.append(
                                                                    f"- Extract from a successful mission{faction} | {task['values'][2]:,}"
                                                                )
                                                            case 9:  # operations
                                                                if task["values"][0] != 0:
                                                                    match task["values"][0]:
                                                                        case 2:
                                                                            faction = " against **Terminids**"
                                                                        case 3:
                                                                            faction = " against **Automatons**"
                                                                        case 4:
                                                                            faction = " against **Illuminate**"
                                                                        case _:
                                                                            faction = " against [Unknown]"
                                                                else:
                                                                    faction = ""
                                                                if (
                                                                    task["valueTypes"][3] == 9
                                                                    and task["values"][3] != 0
                                                                ):
                                                                    for difficulty in data["difficulty"]:
                                                                        if task["values"][3] == difficulty["level"]:
                                                                            diff = f" on **{difficulty['name']}** or higher"
                                                                            break
                                                                        else:
                                                                            diff = " on [UNKNOWN DIFFICULTY LEVEL] or higher"
                                                                else:
                                                                    diff = ""
                                                                objectives.append(
                                                                    f"- Complete Operations{faction}{diff}. | {task['values'][1]:,}"
                                                                )
                                                            case 11:  # liberate
                                                                pindex.append(task["values"][2])
                                                                atype[acount] = 11
                                                                acount += 1
                                                            case 12:  # defend
                                                                if task["values"][1] != 0:
                                                                    match task["values"][1]:
                                                                        case 2:
                                                                            faction = "**Terminid**"
                                                                        case 3:
                                                                            faction = "**Automaton**"
                                                                        case 4:
                                                                            faction = "**Illuminate**"
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
                                                                            pname = f"**{pij['name']}**"
                                                                        else:
                                                                            objectives.append(
                                                                                f"- Defend Planet | {str(task['values'][0])}"
                                                                            )
                                                                    objectives.append(
                                                                        f"- Defend {pname} from {task['values'][0]:,} {['attack', 'attacks'][await self.plural(task['values'][0])]}"
                                                                    )
                                                                objectives.append(
                                                                    f"- Defend Planets{attack} | {str(task['values'][0])}"
                                                                )
                                                            case 13:  # control
                                                                pindex.append(task["values"][2])
                                                                atype[acount] = 13
                                                                acount += 1
                                                            case 15:  # expand
                                                                objectives.append(
                                                                    "- Capture more planets than the enemy."
                                                                )
                                                            case _:
                                                                owner = await self.bot.fetch_user(self.owner_id)
                                                                await owner.send(
                                                                    f"Unknown task type {str(task['type'])}. Aborting..."
                                                                )
                                                                ErrorLogger.run(str(mo))
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
                                                                                        f"- Liberate **{p['name']}**"
                                                                                    )
                                                                                case 13:
                                                                                    objectives.append(
                                                                                        f"- Hold **{p['name']}**"
                                                                                    )
                                                                                case _:
                                                                                    objectives.append(
                                                                                        f"- **{p['name']}**"
                                                                                    )
                                                                break
                                                            else:
                                                                perror = True
                                                                await asyncio.sleep(self.retry)
                                                                continue
                                                    if perror is True and perror is not None:
                                                        owner = await self.bot.fetch_user(self.owner_id)
                                                        await owner.send(f"presponse status code {presponse.status}")
                                                        return
                                                    title = mo["title"] if mo["title"] is not None else ""
                                                    briefing = mo["briefing"] if mo["briefing"] is not None else ""
                                                    desc = mo["description"] if mo["description"] is not None else ""
                                                    exp = round(
                                                        datetime
                                                        .strptime(
                                                            mo["expiration"][:19].strip(),
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
                                                    morder = discord.File(
                                                        self.images["MO"],
                                                        filename="mologo.png",
                                                    )
                                                    emb = await aembed(
                                                        title,
                                                        briefing,
                                                        desc,
                                                        objectives,
                                                        exp,
                                                    )
                                                    msg = await channel.send(files=[morder], embed=emb)
                                                    data["assign_ids"].append(mo["id"])
                                                else:
                                                    continue
                                            for id in data["assign_ids"]:
                                                if id not in molist:
                                                    data["assign_ids"].remove(id)
                                            f.seek(0)
                                            json.dump(data, f, indent=4)
                                            f.truncate()
                                            break
                                        else:
                                            aerror = True
                                            await asyncio.sleep(self.retry)
                                            continue
                                    except (json.JSONDecodeError, client_exceptions.ClientPayloadError):
                                        await asyncio.sleep(self.retry)
                                        continue
                            except (ConnectionAbortedError, asyncio.TimeoutError):
                                ErrorLogger.run(traceback.format_exc())
                                continue
                            except Exception:
                                owner = await self.bot.fetch_user(self.owner_id)
                                await owner.send("Error logged in HD2.")
                                ErrorLogger.run(traceback.format_exc())
                                break
                        if aerror is True and aerror is not None and aresponse.status in self.status_codes:
                            owner = await self.bot.fetch_user(self.owner_id)
                            await owner.send(f"aresponse status code {aresponse.status}")
                    await asyncio.sleep(0)
                await asyncio.sleep(self.update_cooldown)
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
    @app_commands.checks.cooldown(1, 30, key=lambda i: i.guild_id)
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
                regions: list,
            ):
                embed = discord.Embed(color=color)
                embed.title = name
                embed.description = f"{owner} control"
                if liberation:
                    bar1 = "█" * int((math.floor(float(liberation)) / 10))
                    bar3 = "▁" * (10 - len(bar1) - 1)
                if owner == "Super Earth":
                    if event is not None and name != "SUPER EARTH":
                        embed.add_field(name="Attacker:", value=attacker)
                        embed.add_field(name="Attack Origin:", value=attorigin)
                        embed.add_field(name="Time Remaining:", value=time, inline=False)
                        embed.add_field(name="Defense:", value=f"{bar1}▒{bar3} │ {liberation}%")
                    embed.set_thumbnail(url="attachment://faction.png")
                else:
                    embed.add_field(name="Liberation:", value=f"{bar1}▒{bar3} │ {liberation}%")
                    if float(regen) <= 1.5:
                        resistance = "Low"
                    elif float(regen) > 1.5 and float(regen) <= 2:
                        resistance = "Average"
                    elif float(regen) > 2 and float(regen) <= 4:
                        resistance = "High"
                    elif float(regen) > 4:
                        resistance = "Very High"
                    else:
                        resistance = f"ERROR {regen}"
                    embed.add_field(name="Enemy Resistance:", value=f"{regen}% ({resistance})", inline=False)
                    embed.set_thumbnail(url="attachment://faction.png")
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
                if regions != [] and regions is not None:
                    r1 = []
                    for region in regions:
                        if region["name"] is None:
                            continue
                        if (owner != "Super Earth") or (owner == "Super Earth" and event is not None):
                            rlib = math.floor((region["maxHealth"] - region["health"]) / (region["maxHealth"]) * 100)
                            rbar1 = "█" * int(rlib / 10)
                            rbar3 = "▁" * (10 - len(rbar1) - 1)
                            rg = f"{region['name']}\n{rbar1}▒{rbar3} │ {str(rlib)}%"
                        else:
                            rg = region["name"]
                        r1.append(rg)
                    if not r1 == []:
                        r2 = "\n".join(r1)
                        embed.add_field(name="Cities:", value=r2, inline=False)
                embed.set_footer(text=f"{players} Helldivers", icon_url="attachment://hdlogo.png")
                if major is True:
                    embed.set_author(name="MAJOR ORDER", icon_url="attachment://mologo.png")
                return embed

            async def build(planetdata: dict, mo: list):
                embl = []
                embl2 = []
                embl3 = []  # this sucks but I'm lazy
                logo = None
                for planet in planetdata:
                    if planetdata[planet]["index"] in mo:
                        major = True
                    else:
                        major = False
                    if logo is None:
                        logo = planetdata[planet]["logo"]
                    emb = await embed(
                        planet,
                        planetdata[planet]["owner"],
                        planetdata[planet]["lib"],
                        planetdata[planet]["players"],
                        major,
                        planetdata[planet]["time"],
                        planetdata[planet]["attacker"],
                        planetdata[planet]["attorigin"],
                        planetdata[planet]["color"],
                        planetdata[planet]["biome"],
                        planetdata[planet]["hazards"],
                        planetdata[planet]["event"],
                        planetdata[planet]["regen"],
                        planetdata[planet]["regions"],
                    )
                    if len(embl) < 10:
                        embl.append(emb)
                    elif len(embl2) < 10:
                        embl2.append(emb)
                    else:
                        embl3.append(emb)
                    embll = [embl, embl2, embl3]
                for elist in embll:
                    if elist:
                        morder = None
                        files = set()
                        hdlogo = discord.File(self.images["HD"], filename="hdlogo.png")
                        files.add(hdlogo)
                        flogo = discord.File(logo, filename="faction.png")
                        files.add(flogo)
                        for e in elist:
                            if e.author and morder is None:
                                morder = discord.File(self.images["MO"], filename="mologo.png")
                                files.add(morder)
                                break
                        await interaction.followup.send(files=files, embeds=elist)

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
                                        planetdata = {}
                                        index = p["index"]
                                        name = p["name"]
                                        owner = p["currentOwner"]
                                        players = p["statistics"]["playerCount"]
                                        biome = p["biome"]
                                        hazards = p["hazards"]
                                        regions = p["regions"]
                                        if owner == "Humans":
                                            owner = "Super Earth"
                                            regen = None
                                            color = self.colors["SE"]
                                            logo = self.images["SE"]
                                            if p["event"] is not None:
                                                event = True
                                                end = (
                                                    datetime
                                                    .strptime(
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
                                                lib = None
                                                attacker = None
                                                attorigin = None
                                                time = None
                                        else:
                                            lib = str(
                                                round(
                                                    float((p["maxHealth"] - p["health"]) / (p["maxHealth"]) * 100),
                                                    5,
                                                )
                                            )
                                            regen = str(
                                                "{:.2f}".format(
                                                    round(((p["regenPerSecond"] * 3600) / p["maxHealth"]) * 100, 2)
                                                )
                                            )
                                            match owner:
                                                case "Terminids":
                                                    owner = "Terminid"
                                                    color = self.colors["TR"]
                                                    logo = self.images["TR"]
                                                case "Automaton":
                                                    color = self.colors["AT"]
                                                    logo = self.images["AT"]
                                                case "Illuminate":
                                                    color = self.colors["IL"]
                                                    logo = self.images["IL"]
                                            time = None
                                            attacker = None
                                            attorigin = None
                                            event = None
                                        planetdata.update({
                                            name: {
                                                "index": index,
                                                "lib": lib,
                                                "owner": owner,
                                                "time": time,
                                                "attacker": attacker,
                                                "attorigin": attorigin,
                                                "color": color,
                                                "players": players,
                                                "biome": biome,
                                                "hazards": hazards,
                                                "event": event,
                                                "regen": regen,
                                                "regions": regions,
                                                "logo": logo,
                                            }
                                        })
                                        await build(planetdata, mo)
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
                                regions = planet["regions"]
                                if owner == "Humans" and index != 0:
                                    end = (
                                        datetime
                                        .strptime(
                                            planet["event"]["endTime"][:19].strip(),
                                            "%Y-%m-%dT%H:%M:%S",
                                        )
                                        .replace(tzinfo=timezone.utc)
                                        .astimezone(tz=None)
                                    )
                                    now = datetime.now(UTC)
                                    rdelta = relativedelta(end, now)
                                    time = f"{rdelta.days}D:{rdelta.hours}H:{rdelta.minutes}M:{rdelta.seconds}S"
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
                                    seplanetdata.update({
                                        name: {
                                            "index": index,
                                            "lib": lib,
                                            "owner": "Super Earth",
                                            "time": time,
                                            "attacker": attacker,
                                            "attorigin": attorigin,
                                            "color": self.colors["SE"],
                                            "players": players,
                                            "biome": biome,
                                            "hazards": hazards,
                                            "event": True,
                                            "regen": None,
                                            "regions": regions,
                                            "logo": self.images["SE"],
                                        }
                                    })
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
                                        "{:.2f}".format(
                                            round(((planet["regenPerSecond"] * 3600) / planet["maxHealth"]) * 100, 2)
                                        )
                                    )
                                    match owner:
                                        case "Humans":
                                            seplanetdata.update({
                                                name: {
                                                    "index": index,
                                                    "owner": "Super Earth",
                                                    "lib": lib,
                                                    "players": players,
                                                    "time": None,
                                                    "attacker": None,
                                                    "attorigin": None,
                                                    "color": self.colors["SE"],
                                                    "biome": biome,
                                                    "hazards": hazards,
                                                    "event": None,
                                                    "regen": None,
                                                    "regions": regions,
                                                    "logo": self.images["SE"],
                                                }
                                            })
                                        case "Automaton":
                                            aplanetdata.update({
                                                name: {
                                                    "index": index,
                                                    "owner": owner,
                                                    "lib": lib,
                                                    "players": players,
                                                    "time": None,
                                                    "attacker": None,
                                                    "attorigin": None,
                                                    "color": self.colors["AT"],
                                                    "biome": biome,
                                                    "hazards": hazards,
                                                    "event": None,
                                                    "regen": regen,
                                                    "regions": regions,
                                                    "logo": self.images["AT"],
                                                }
                                            })
                                        case "Terminids":
                                            tplanetdata.update({
                                                name: {
                                                    "index": index,
                                                    "owner": "Terminid",
                                                    "lib": lib,
                                                    "players": players,
                                                    "time": None,
                                                    "attacker": None,
                                                    "attorigin": None,
                                                    "color": self.colors["TR"],
                                                    "biome": biome,
                                                    "hazards": hazards,
                                                    "event": None,
                                                    "regen": regen,
                                                    "regions": regions,
                                                    "logo": self.images["TR"],
                                                }
                                            })
                                        case "Illuminate":
                                            iplanetdata.update({
                                                name: {
                                                    "index": index,
                                                    "owner": owner,
                                                    "lib": lib,
                                                    "players": players,
                                                    "time": None,
                                                    "attacker": None,
                                                    "attorigin": None,
                                                    "color": self.colors["IL"],
                                                    "biome": biome,
                                                    "hazards": hazards,
                                                    "event": None,
                                                    "regen": regen,
                                                    "regions": regions,
                                                    "logo": self.images["IL"],
                                                }
                                            })
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
                            for pdata in [aplanetdata, tplanetdata, iplanetdata, seplanetdata]:
                                if pdata != {}:
                                    await build(pdata, mo)
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
    @app_commands.checks.cooldown(1, 30, key=lambda i: i.guild_id)
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
                aerror = True
                for i in range(3):
                    try:
                        async with session.get(f"{self.api}/assignments") as aresponse:
                            try:
                                if aresponse.status == 200:
                                    aj = await aresponse.json()
                                    aerror = False
                                    if aj == []:
                                        await interaction.followup.send("Major Order not found.")
                                        return
                                    for mo in aj:
                                        objectives = []
                                        prog = mo["progress"]
                                        tasks = mo["tasks"]
                                        pindex = []
                                        atype = {}
                                        acount = 0
                                        index = 0
                                        for task in tasks:
                                            match task["type"]:
                                                case 2:  # collect
                                                    if task["valueTypes"][4] == 5 and task["values"][4] != 0:
                                                        with open(self.file, "r", encoding="utf-8") as f:
                                                            data = json.load(f)
                                                            for sample in data["sample_ids"]:
                                                                if task["values"][4] == sample["id"]:
                                                                    samples = f"**{sample['sample']}**"
                                                    else:
                                                        sample = "Unknown Samples"
                                                    if task["valueTypes"][8] == 12 and task["values"][8] != 0:
                                                        async with session.get(
                                                            f"{self.api}/planets/{task['values'][8]}"
                                                        ) as psresponse:
                                                            psj = await psresponse.json()
                                                            if psresponse.status == 200:
                                                                pname = f" on **{psj['name']}**"
                                                    elif task["values"][8] == 0 and task["values"][0] != 0:
                                                        match task["values"][0]:
                                                            case 2:
                                                                pname = " on Terminid controlled planets"
                                                            case 3:
                                                                pname = " on Automaton controlled planets"
                                                            case 4:
                                                                pname = " on Illuminate controlled planets"
                                                            case _:
                                                                pname = ""
                                                    else:
                                                        pname = ""
                                                    goal = task["values"][2]
                                                    objectives.append(
                                                        f"- Collect {samples}{pname}\n{prog[index]:,} / {goal:,} - {str(round(float((prog[index] / goal) * 100), 1))}%"
                                                    )
                                                case 3:  # eradicate
                                                    if task["valueTypes"][3] == 4 and task["values"][3] != 0:
                                                        with open(self.file, "r", encoding="utf-8") as f:
                                                            data = json.load(f)
                                                            for target in data["target_ids"]:
                                                                if task["values"][3] == target["id"]:
                                                                    target = f"**{target['target']}**"
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
                                                                target = "**Terminids**"
                                                            case 3:
                                                                target = "**Automatons**"
                                                            case 4:
                                                                target = "**Illuminate**"
                                                            case _:
                                                                target = "Enemies"
                                                    if task["valueTypes"][5] == 5 and task["values"][5] != 0:
                                                        with open(self.file, "r", encoding="utf-8") as f:
                                                            data = json.load(f)
                                                            for weapon in data["weapon_ids"]:
                                                                if task["values"][5] == weapon["id"]:
                                                                    t2 = f"with the **{weapon['weapon']}**"
                                                                    break
                                                                else:
                                                                    t2 = "with a specific weapon"
                                                            target = f"{target} {t2}"
                                                    if task["valueTypes"][9] == 12 and task["values"][9] != 0:
                                                        async with session.get(
                                                            f"{self.api}/planets/{task['values'][9]}"
                                                        ) as piresponse:
                                                            pij = await piresponse.json()
                                                            if piresponse.status == 200:
                                                                pname = f" on **{pij['name']}**"
                                                    else:
                                                        pname = ""
                                                    goal = task["values"][2]
                                                    objectives.append(
                                                        f"- Eradicate {target}{pname}\n{prog[index]:,} / {goal:,} - {str(round(float((prog[index] / goal) * 100), 1))}%"
                                                    )
                                                case 7:  # extract
                                                    goal = task["values"][2]
                                                    if task["values"][0] != 0:
                                                        match task["values"][0]:
                                                            case 2:
                                                                faction = " against **Terminids**"
                                                            case 3:
                                                                faction = " against **Automatons**"
                                                            case 4:
                                                                faction = " against **Illuminate**"
                                                            case _:
                                                                faction = " against [Unknown]"
                                                    else:
                                                        faction = ""
                                                    objectives.append(
                                                        f"- Extract from a successful mission{faction}\n{prog[index]:,} / {goal:,} - {str(round(float((prog[index] / goal) * 100), 1))}%"
                                                    )
                                                case 9:  # operations
                                                    goal = task["values"][1]
                                                    if task["values"][0] != 0:
                                                        match task["values"][0]:
                                                            case 2:
                                                                faction = " against **Terminids**"
                                                            case 3:
                                                                faction = " against **Automatons**"
                                                            case 4:
                                                                faction = " against **Illuminate**"
                                                            case _:
                                                                faction = " against [Unknown]"
                                                    else:
                                                        faction = ""
                                                    if task["valueTypes"][3] == 9 and task["values"][3] != 0:
                                                        with open(self.file, "r", encoding="utf-8") as f:
                                                            data = json.load(f)
                                                            for difficulty in data["difficulty"]:
                                                                if task["values"][3] == difficulty["level"]:
                                                                    diff = f" on **{difficulty['name']}** or higher"
                                                                    break
                                                                else:
                                                                    diff = " on [UNKNOWN DIFFICULTY LEVEL] or higher"
                                                    else:
                                                        diff = ""
                                                    objectives.append(
                                                        f"- Complete Operations{faction}{diff}\n{prog[index]:,} / {goal:,} - {str(round(float((prog[index] / goal) * 100), 1))}%"
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
                                                                faction = "**Terminid**"
                                                            case 3:
                                                                faction = "**Automaton**"
                                                            case 4:
                                                                faction = "**Illuminate**"
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
                                                                pname = f"**{pij['name']}**"
                                                            else:
                                                                objectives.append(
                                                                    f"- Defend Planet from {goal:,} {['attack', 'attacks'][await self.plural(goal)]}\n{prog[index]} / {goal} - {str(round(float((prog[index] / goal) * 100), 1))}%"
                                                                )
                                                        objectives.append(
                                                            f"- Defend {pname} from {goal:,} {['attack', 'attacks'][await self.plural(goal)]}\n{prog[index]} / {goal} - {str(round(float((prog[index] / goal) * 100), 1))}%"
                                                        )
                                                    else:
                                                        objectives.append(
                                                            f"- Defend Planets{attack}\n{prog[index]:,} / {goal:,} - {str(round(float((prog[index] / goal) * 100), 1))}%"
                                                        )
                                                case 13:  # control
                                                    pindex.append(task["values"][2])
                                                    atype[acount] = 13
                                                    acount += 1
                                                case 15:  # expand
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
                                                        f"- Capture more planets than the enemy.\n{bar1}│{bar2}"
                                                    )
                                                case _:
                                                    await interaction.followup.send(
                                                        f"Unknown task type {str(task['type'])}. Aborting..."
                                                    )
                                                    ErrorLogger.run(str(mo))
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
                                                                    name = f"**{p['name']}** | {lib}%"
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
                                                                        name = f"**{p['name']}** | ⚠ {lib}%"
                                                                    else:
                                                                        name = f"**{p['name']}** | ✓"
                                                                match atype[i]:
                                                                    case 11:
                                                                        objectives.append(f"- Liberate {name}")
                                                                    case 13:
                                                                        objectives.append(f"- Hold {name}")
                                                                    case _:
                                                                        objectives.append(name)
                                                else:
                                                    perror = True
                                                    await asyncio.sleep(self.retry)
                                                    continue
                                            if perror is True and perror is not None:
                                                await interaction.followup.send(
                                                    f"presponse status code {presponse.status}"
                                                )
                                        title = mo["title"] if mo["title"] is not None else ""
                                        briefing = mo["briefing"] if mo["briefing"] is not None else ""
                                        desc = mo["description"] if mo["description"] is not None else ""
                                        exp = round(
                                            datetime
                                            .strptime(
                                                mo["expiration"][:19].strip(),
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
                                        morder = discord.File(
                                            self.images["MO"],
                                            filename="mologo.png",
                                        )
                                        emb = await embed(title, briefing, desc, objectives, exp)
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
                    await interaction.followup.send(f"aresponse status code {aresponse.status}. Failed after 3 tries.")
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
