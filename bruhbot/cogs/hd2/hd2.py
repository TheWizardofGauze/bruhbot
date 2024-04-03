import asyncio
import json
import os
from requests import get, exceptions
import traceback

import discord
from dotenv import load_dotenv
from redbot.core import commands, app_commands

from bruhbot import ErrorLogger


class HD2(commands.Cog):
    bot = commands.Bot(command_prefix="$", intents=discord.Intents.default())

    def __init__(self, bot):
        self.bot = bot
        # self.api = "https://helldivers-2.fly.dev/api"
        self.api = "https://helldivers-2-dotnet.fly.dev/api/v1"
        self.here = os.path.dirname(__file__)
        self.file = f"{self.here}\\hd2.json"
        load_dotenv(os.path.abspath(".\\bruhbot\\.env"))
        self.owner_id = int(os.getenv("OWNER_ID"))

    async def get_war_id(self):
        response = get(self.api)
        if response.status_code == 200:
            war_id = response.json()["current"]
            return war_id

    async def update(self):
        try:

            async def dembed(
                message: str,
            ):
                embed = discord.Embed(color=discord.Color.light_grey())
                embed.title = "NEW DISPATCH FROM SUPER EARTH"
                embed.description = message
                return embed

            async def aembed(
                title: str, briefing: str, description: str, planets: list, reward: str
            ):
                planet = "\n".join(planets)
                embed = discord.Embed(color=discord.Color.dark_grey())
                embed.title = title
                embed.description = briefing
                embed.add_field(name=description, value=planet)
                embed.set_footer(text=f"REWARD: {reward} MEDALS")
                return embed

            while True:
                with open(self.file, "r+", encoding="utf-8") as f:
                    dump = False
                    data = json.load(f)
                    channel = self.bot.get_channel(data["servers"][0]["cid"])
                    try:
                        dresponse = get(f"{self.api}/dispatches")
                        if dresponse.status_code == 200:
                            for d in dresponse.json():
                                if d["id"] > data["dispatch_id"]:
                                    emb = await dembed(message=d["message"])
                                    await channel.send(embed=emb)
                                    data["dispatch_id"] = d["id"]
                                else:
                                    continue
                                if not d["id"] == data["dispatch_id"]:
                                    dump = True
                        else:
                            owner = await self.bot.fetch_user(self.owner_id)
                            await owner.send(
                                f"{dresponse.status_code}\n{dresponse.json()}"
                            )
                    except exceptions.JSONDecodeError:
                        pass
                    try:
                        aresponse = get(f"{self.api}/assignments")
                        aj = aresponse.json()
                        pindex = []
                        planets = []
                        if aresponse.status_code == 200:
                            if aj[0]["id"] != data["assign_id"]:
                                for t in aj[0]["tasks"]:
                                    pindex.append(t["values"][2])
                                for p in pindex:
                                    presponse = get(f"{self.api}/planets/{p}")
                                    planets.append(f"-{presponse.json()['name']}")
                                title = aj[0]["title"]
                                briefing = aj[0]["briefing"]
                                desc = aj[0]["description"]
                                reward = aj[0]["reward"]["amount"]
                                emb = await aembed(
                                    title, briefing, desc, planets, reward
                                )
                                await channel.send(embed=emb)
                                data["assign_id"] = aj[0]["id"]
                                dump = True
                        else:
                            owner = await self.bot.fetch_user(self.owner_id)
                            await owner.send(
                                f"{dresponse.status_code}\n{dresponse.json()}"
                            )
                    except exceptions.JSONDecodeError:
                        pass
                    if dump is True:
                        f.seek(0)
                        json.dump(data, f, indent=4)
                        f.truncate()
                asyncio.sleep(3600)
        except Exception:
            owner = await self.bot.fetch_user(self.owner_id)
            await owner.send("Error logged in HD2.")
            ErrorLogger.run(traceback.format_exc())

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
                color: discord.Color,
            ):
                embed = discord.Embed(color=color)
                embed.title = name
                embed.description = f"{owner} control"
                if owner == "Super Earth":
                    embed.add_field(name="Defense Campaign", value="")
                    embed.set_thumbnail(url="attachment://selogo.png")
                else:
                    embed.add_field(name="Liberation:", value=f"{liberation}%")
                    if owner == "Automaton":
                        embed.set_thumbnail(url="attachment://alogo.png")
                    elif owner == "Terminid":
                        embed.set_thumbnail(url="attachment://tlogo.png")
                embed.set_footer(
                    text=f"{players} Helldivers", icon_url="attachment://hdlogo.png"
                )
                if major is True:
                    embed.set_author(name="MAJOR ORDER")
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
                    lib = str(
                        (
                            (int(planet["maxHealth"]) - int(planet["health"]))
                            / int(planet["maxHealth"])
                            * 100
                        )
                    )
                    owner = planet["currentOwner"]
                    players = planet["statistics"]["playerCount"]
                    planetdata.update(
                        {
                            name: {
                                "index": index,
                                "lib": lib,
                                "owner": owner,
                                "players": players,
                            }
                        }
                    )
                aresponse = get(f"{self.api}/assignments")
                mo = []
                for t in aresponse.json()[0]["tasks"]:
                    mo.append(t["values"][2])
                embl = []
                files = set()
                selogo = discord.File(
                    f"{self.here}\\SuperEarth.png", filename="selogo.png"
                )
                alogo = discord.File(
                    f"{self.here}\\Automaton.png", filename="alogo.png"
                )
                tlogo = discord.File(f"{self.here}\\Terminid.png", filename="tlogo.png")
                hdlogo = discord.File(
                    f"{self.here}\\Helldivers.png",
                    filename="hdlogo.png",
                )
                files.add(hdlogo)
                for planet in planetdata:
                    major = True if planetdata[planet]["index"] in mo else False
                    if planetdata[planet]["owner"] == "Humans":
                        powner = "Super Earth"
                        color = 0x05E7F3
                        files.add(selogo)
                    elif planetdata[planet]["owner"] == "Automaton":
                        powner = "Automaton"
                        color = 0xF11901
                        files.add(alogo)
                    elif planetdata[planet]["owner"] == "Terminids":
                        powner = "Terminid"
                        color = 0xFEE75C
                        files.add(tlogo)
                    plib = (
                        "DEFENSE CAMPAIGN"
                        if powner == "Super Earth"
                        else planetdata[planet]["lib"]
                    )
                    emb = await embed(
                        planet,
                        powner,
                        plib,
                        planetdata[planet]["players"],
                        major,
                        color,
                    )
                    embl.append(emb)
                await interaction.followup.send(files=files, embeds=embl)

            else:
                await interaction.send(f"{cresponse.status_code}\n{cresponse.json()}")
                return
        except Exception:
            owner = await self.bot.fetch_user(self.owner_id)
            await owner.send("Error logged in HD2.")
            ErrorLogger.run(traceback.format_exc())

    @status.error
    async def status_error(self, interaction: discord.Interaction, error):
        if isinstance(error, commands.CommandOnCooldown):
            await interaction.response.send(
                f"Command on cooldown, try again in {error.retry_after: .0f} seconds.",
                ephemeral=True,
            )
