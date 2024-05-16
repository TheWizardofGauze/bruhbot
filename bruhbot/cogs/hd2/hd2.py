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
                    for i in range(3):  # dresponse
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
                    for i in range(3):  # aresponse
                        try:
                            aresponse = get(
                                f"{self.api}/assignments", headers=self.headers
                            )
                            try:
                                objectives = []
                                if aresponse.status_code == 200:
                                    aerror = False
                                    if aresponse.json() == []:
                                        ErrorLogger.run("aresponse returned empty.")
                                        break
                                    aj = aresponse.json()[0]
                                    task = aj["tasks"][0]
                                    if aj["id"] != data["assign_id"]:
                                        if task["type"] == 3:
                                            objectives.append(f"{task['values'][2]:,}")
                                        elif task["type"] == 12:
                                            # write more permanent fix, type 3 seems to be "Kill X of Y", need to find what type liberation orders are. probably don't need to display anything other than the order description for type 3. ["values"] may be [faction, <unknown>, goal]
                                            # Type 12 may be defense. ["values"][0] Seems to be the goal. Probably won't use since it's in the assignment description usually.
                                            # Type 11 should be liberation. ["values"][2] is planet index.
                                            objectives.append(str(task["values"][0]))
                                        else:
                                            pindex = []
                                            for t in aj["tasks"]:
                                                pindex.append(t["values"][2])
                                            for p in pindex:
                                                presponse = get(
                                                    f"{self.api}/planets/{p}",
                                                    headers=self.headers,
                                                )
                                                objectives.append(
                                                    f"-{presponse.json()['name']}"
                                                )
                                        title = aj["title"]
                                        briefing = aj["briefing"]
                                        desc = aj["description"]
                                        exp = round(
                                            datetime.strptime(
                                                aj["expiration"][:19].strip(),
                                                "%Y-%m-%dT%H:%M:%S",
                                            ).timestamp()
                                        )
                                        for tag in tags:
                                            title = title.replace(tag, "**")
                                            briefing = briefing.replace(tag, "**")
                                            desc = desc.replace(tag, "**")
                                        if aj["reward"]["type"] == 1:
                                            reward = aj["reward"]["amount"]
                                        else:
                                            owner = await self.bot.fetch_user(
                                                self.owner_id
                                            )
                                            await owner.send(
                                                f"Unknown reward type {str(aj['reward']['type'])}"
                                            )
                                            return
                                        morder = discord.File(
                                            f"{self.here}\\MajorOrder.png",
                                            filename="mologo.png",
                                        )
                                        micon = discord.File(
                                            f"{self.here}\\Medal.png",
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
                                        msg = await channel.send(
                                            files=[morder, micon], embed=emb
                                        )
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

    @hd2.command(
        name="warstatus",
        description="Get current Galactic War status for Helldivers 2.",
    )
    @app_commands.checks.cooldown(1, 60, key=lambda i: (i.guild_id))
    async def warstatus(self, interaction: discord.Interaction):
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
            ):
                embed = discord.Embed(color=color)
                embed.title = name
                embed.description = f"{owner} control"
                if owner == "Super Earth":
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
            for i in range(3):  # cresponse
                cresponse = get(f"{self.api}/campaigns", headers=self.headers)
                if cresponse.status_code == 200:
                    cerror = False
                    if cresponse.json() == []:
                        await interaction.followup.send("cresponse returned empty.")
                        return
                    planets = []
                    aplanetdata = {}
                    tplanetdata = {}
                    iplanetdata = {}
                    seplanetdata = {}
                    for c in cresponse.json():
                        planets.append(c["planet"])
                    for planet in planets:
                        index = planet["index"]
                        name = planet["name"]

                        owner = planet["currentOwner"]
                        players = planet["statistics"]["playerCount"]
                        biome = planet["biome"]
                        hazards = planet["hazards"]
                        if owner == "Humans":
                            end = datetime.strptime(
                                planet["event"]["endTime"][:19].strip(),
                                "%Y-%m-%dT%H:%M:%S",
                            )
                            attacker = planet["event"]["faction"].replace(
                                "Automaton", "Automatons"
                            )
                            lib = str(
                                round(
                                    float(
                                        (
                                            planet["event"]["maxHealth"]
                                            - planet["event"]["health"]
                                        )
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
                                        (planet["maxHealth"] - planet["health"])
                                        / (planet["maxHealth"])
                                        * 100
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

                    if not aplanetdata == {}:
                        aembl = []
                        afiles = set()
                        hdlogo = discord.File(
                            f"{self.here}\\Helldivers.png",
                            filename="hdlogo.png",
                        )
                        afiles.add(hdlogo)
                        alogo = discord.File(
                            f"{self.here}\\Automaton.png", filename="alogo.png"
                        )
                        afiles.add(alogo)
                        for planet in aplanetdata:
                            if aplanetdata[planet]["index"] in mo:
                                major = True
                                morder = discord.File(
                                    f"{self.here}\\MajorOrder.png",
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
                            )
                            aembl.append(emb)
                        await interaction.followup.send(files=afiles, embeds=aembl)
                    if not tplanetdata == {}:
                        tembl = []
                        tfiles = set()
                        hdlogo = discord.File(
                            f"{self.here}\\Helldivers.png",
                            filename="hdlogo.png",
                        )
                        tfiles.add(hdlogo)
                        tlogo = discord.File(
                            f"{self.here}\\Terminid.png", filename="tlogo.png"
                        )
                        tfiles.add(tlogo)
                        for planet in tplanetdata:
                            if tplanetdata[planet]["index"] in mo:
                                major = True
                                morder = discord.File(
                                    f"{self.here}\\MajorOrder.png",
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
                            )
                            tembl.append(emb)
                        await interaction.followup.send(files=tfiles, embeds=tembl)
                    if not iplanetdata == {}:
                        iembl = []
                        ifiles = set()
                        hdlogo = discord.File(
                            f"{self.here}\\Helldivers.png",
                            filename="hdlogo.png",
                        )
                        ifiles.add(hdlogo)
                        ilogo = discord.File(
                            f"{self.here}\\Illuminate.png", filename="ilogo.png"
                        )
                        ifiles.add(ilogo)
                        for planet in iplanetdata:
                            if iplanetdata[planet]["index"] in mo:
                                major = True
                                morder = discord.File(
                                    f"{self.here}\\MajorOrder.png",
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
                            )
                            iembl.append(emb)
                        await interaction.followup.send(files=ifiles, embeds=iembl)
                    if not seplanetdata == {}:
                        seembl = []
                        sefiles = set()
                        hdlogo = discord.File(
                            f"{self.here}\\Helldivers.png",
                            filename="hdlogo.png",
                        )
                        sefiles.add(hdlogo)
                        selogo = discord.File(
                            f"{self.here}\\SuperEarth.png", filename="selogo.png"
                        )
                        sefiles.add(selogo)
                        for planet in seplanetdata:
                            if seplanetdata[planet]["index"] in mo:
                                major = True
                                morder = discord.File(
                                    f"{self.here}\\MajorOrder.png",
                                    filename="mologo.png",
                                )
                                sefiles.add(morder)
                            else:
                                major = False
                            now = datetime.now()
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
                            )
                            seembl.append(emb)
                        await interaction.followup.send(files=sefiles, embeds=seembl)

                else:
                    cerror = True
                    await asyncio.sleep(15)
                    continue
                break
            if cerror is True:
                await interaction.followup.send(
                    f"cresponse status code {cresponse.status_code}. Failed after 3 tries."
                )
                return
        except Exception:
            await interaction.followup.send("Error logged in HD2.")
            ErrorLogger.run(traceback.format_exc())

    @warstatus.error
    async def warstatus_error(self, interaction: discord.Interaction, error):
        if isinstance(error, commands.CommandOnCooldown):
            await interaction.response.send(
                f"Command on cooldown, try again in {error.retry_after: .0f} seconds.",
                ephemeral=True,
            )

    @hd2.command(
        name="mostatus", description="Get current Major Order status for Helldivers 2."
    )
    @app_commands.checks.cooldown(1, 60, key=lambda i: (i.guild_id))
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
                    embed.add_field(
                        name="Expires:", value=f"<t:{expire}:R>", inline=False
                    )
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
            tags = ["<i=1>", "<i=3>", "</i>"]
            for i in range(3):
                try:
                    aresponse = get(f"{self.api}/assignments", headers=self.headers)
                    try:
                        aj = aresponse.json()[0]
                        task = aj["tasks"][0]
                        objectives = []
                        if aresponse.status_code == 200:
                            aerror = False
                            if aj == []:
                                await interaction.followup.send(
                                    "Major Order not found."
                                )
                                return
                            if task["type"] == 3:
                                prog = aj["progress"][0]
                                goal = task["values"][2]
                                objectives.append(
                                    f"{prog:,}/{goal:,} - {str(round(float((prog/goal)*100),1))}%"
                                )
                            elif task["type"] == 12:
                                prog = aj["progress"][0]
                                goal = task["values"][0]
                                objectives.append(
                                    f"{prog}/{goal} - {str(round(float((prog/goal)*100),1))}%"
                                )
                            elif task["type"] == 11:
                                pindex = []
                                prog = aj["progress"]
                                for t in aj["tasks"]:
                                    pindex.append(t["values"][2])
                                for i, p in enumerate(pindex):
                                    presponse = get(
                                        f"{self.api}/planets/{p}",
                                        headers=self.headers,
                                    )
                                    if prog[i] == 0:
                                        name = f"-{presponse.json()['name']}"
                                    elif prog[i] == 1:
                                        name = f"~~-{presponse.json()['name']}~~"
                                    objectives.append(name)
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
                                ).timestamp()
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
                                f"{self.here}\\MajorOrder.png",
                                filename="mologo.png",
                            )
                            micon = discord.File(
                                f"{self.here}\\Medal.png",
                                filename="medal.png",
                            )
                            emb = await embed(
                                title, briefing, desc, objectives, reward, exp
                            )
                            await interaction.followup.send(
                                files=[morder, micon], embed=emb
                            )
                            break
                        else:
                            aerror = True
                            await asyncio.sleep(15)
                            continue
                    except exceptions.JSONDecodeError:
                        await asyncio.sleep(15)
                        continue
                except Exception:
                    await interaction.followup.send("Error logged in HD2.")
                    ErrorLogger.run(traceback.format_exc())
                    break
            if aerror is True and aerror is not None:
                await interaction.followup.send(
                    f"aresponse status code {aresponse.status_code}"
                )
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
