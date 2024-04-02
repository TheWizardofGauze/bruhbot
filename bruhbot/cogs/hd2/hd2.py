import asyncio
import json
import os
from requests import get
import traceback

import discord
from dotenv import load_dotenv
from redbot.core import commands, app_commands

from bruhbot import ErrorLogger


class HD2(commands.Cog):
    bot = commands.Bot(command_prefix="$", intents=discord.Intents.default())

    def __init__(self, bot):
        self.bot = bot
        self.api = "https://helldivers-2.fly.dev/api"
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
            while True:
                with open(self.file, "r+", encoding="utf-8") as f:
                    war_id = await self.get_war_id()
                    data = json.load(f)
                    eresponse = get(f"{self.api}/{war_id}/events")
                    if eresponse.status_code == 200:
                        if eresponse.json() == []:
                            return
                        event = eresponse.json()[0]["message"]["en"]
                        if event == data["event"]:
                            return
                        channel = self.bot.get_channel(data["servers"]["cid"])
                        await channel.send(str(event))
                        data["event"] = event
                        f.seek(0)
                        json.dump(data, f, indent=4)
                        f.truncate()
                    else:
                        owner = await self.bot.fetch_user(self.owner_id)
                        await owner.send(f"{eresponse.status_code}\n{eresponse.json()}")
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
                return embed

            await interaction.response.defer()
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
                    else:
                        await interaction.followup.send(
                            f"{presponse.status_code}\n{presponse.json()}",
                            ephemeral=True,
                        )
                        return
                embl = []
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
                for planet in planetdata:
                    if planetdata[planet]["owner"] == "Humans":
                        powner = "Super Earth"
                        color = 0x05E7F3
                    elif planetdata[planet]["owner"] == "Automaton":
                        powner = "Automaton"
                        color = 0xF11901
                    elif planetdata[planet]["owner"] == "Terminids":
                        powner = "Terminid"
                        color = 0xFEE75C
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
                        color,
                    )
                    embl.append(emb)
                await interaction.followup.send(
                    files=[selogo, alogo, tlogo, hdlogo], embeds=embl
                )

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
