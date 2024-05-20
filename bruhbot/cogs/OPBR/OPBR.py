from contextlib import suppress
from datetime import datetime
import json
import os
import traceback

from dateutil.relativedelta import relativedelta
import discord
from redbot.core import commands
from wikidata.client import Client

from bruhbot import ErrorLogger


class Cont(Exception):
    pass


class OPBR(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.file = f"{os.path.dirname(__file__)}\\opbr.json"
        self.title = "*Old Person Battle Royale*"
        self.url = "https://jamboard.google.com/d/1DikJQQONWUW7odKQoFLlrcri_li4DxVvcyZ_kkfJ77M/edit?usp=sharing"

    async def get_names(self, mode: int):
        if mode == 0:
            with open(self.file) as f:
                data = json.load(f)
                names = []
                for name in data["names"]:
                    if data[name]["dead"] == 0:
                        names.append(name)
        elif mode == 1:
            with open(self.file) as f:
                data = json.load(f)
                names = []
                for name in data["names"]:
                    names.append(name)
        return names

    async def get_color(self, ctx):
        color = (
            ctx.guild.get_member(self.bot.user.id).top_role.color
            if ctx.guild
            else 0xE74C3C  # red
        )
        return color

    @commands.hybrid_group()
    async def opbr(self, ctx):
        """
        The Old Person Battle Royale.

        View stats and check for updates in the Old Person Battle Royale.
        """
        if ctx.invoked_subcommand is None:
            return

    @opbr.command()
    async def update(self, ctx):
        """
        Update the battle royale.

        Check if any contestants got older or died via Wikidata.
        """
        try:
            async with ctx.typing():
                names = await self.get_names(0)
                color = await self.get_color(ctx)
                new = False
                winner = False
                remaining = len(names)
                today = datetime.today()
                cont = Cont()
                client = Client()
                with open(self.file, "r+") as f:
                    data = json.load(f)
                    for name in names:
                        try:
                            contestant = client.get(data[name]["id"])
                            birth_date = contestant[client.get("P569")]
                            with suppress(KeyError):
                                death_date = contestant[client.get("P570")]
                                if death_date is not None:
                                    new = True
                                    age = relativedelta(death_date, birth_date).years
                                    remaining -= 1
                                    if remaining != 1:
                                        foot = f"{remaining} contestants remain."
                                    else:
                                        foot = f"{remaining} contestant remains."
                                        winner = True
                                    if remaining == 0:
                                        deathDesc = f"**The champion has fallen!**\n{name} has died at age {age}."
                                    else:
                                        deathDesc = f"**A contestant has fallen!**\n{name} has died at age {age}."
                                    msg = discord.Embed(
                                        title=self.title,
                                        description=deathDesc,
                                        color=color,
                                        url=self.url,
                                    )
                                    msg.set_footer(text=foot)
                                    await ctx.send(embed=msg)
                                    data[name]["age"] = age
                                    data[name]["dead"] = 1
                                    f.seek(0)
                                    json.dump(data, f, indent=4)
                                    f.truncate()
                                    raise cont
                            age = relativedelta(today, birth_date).years
                            if not int(data[name]["age"]) == age:
                                new = True
                                msg = discord.Embed(
                                    title=self.title,
                                    description=f"**A contestant has advanced!**\n{name} is now {age} years old.",
                                    color=color,
                                    url=self.url,
                                )
                                await ctx.send(embed=msg)
                                data[name]["age"] = age
                                f.seek(0)
                                json.dump(data, f, indent=4)
                                f.truncate()
                        except Cont:
                            continue
                    data["updated"] = today.strftime("%m/%d/%Y %I:%M %p")
                    f.seek(0)
                    json.dump(data, f, indent=4)
                    f.truncate()
            if new is False:
                await ctx.send("No new updates.")
            if winner is True:
                names = await self.get_names(0)
                winner = names[0]
                msg = discord.Embed(
                    title=self.title,
                    description=f"**Victory Royale!**\n{winner} has won the battle royale at {age} years old.",
                    color=color,
                    url=self.url,
                )
                await ctx.send(embed=msg)
        except Exception:
            ErrorLogger.run(traceback.format_exc())
            await ctx.send("Update failed! Error logged.")

    @opbr.group(fallback="current", invoke_without_command=True)
    async def stats(self, ctx):
        """
        Show battle royale stats.

        Displays list of contestants ordered from oldest to youngest.
        """
        if ctx.invoked_subcommand is None:
            try:
                combined = []
                names = await self.get_names(0)
                color = await self.get_color(ctx)
                with open(self.file) as f:
                    data = json.load(f)
                    for name in names:
                        combo = f"{name}, **{data[name]['age']}**"
                        combined.append(combo)
                    combined.sort(
                        key=lambda x: int(x.partition("*")[-1].strip("*")),
                        reverse=True,
                    )
                    content = "\n".join(combined)
                    msg = discord.Embed(
                        title=self.title,
                        description=f"**__Contestants__**\n{content}",
                        color=color,
                        url=self.url,
                    ).set_footer(text=f"Last updated {data['updated']}")
                    await ctx.send(embed=msg)
            except Exception:
                ErrorLogger.run(traceback.format_exc())
                await ctx.send("Error logged in OPBR.")

    @stats.command()
    async def all(self, ctx):
        """
        Show full battle royale stats.

        Displays list of all contestants, living or dead.
        """
        try:
            combined = []
            names = await self.get_names(1)
            color = await self.get_color(ctx)
            with open(self.file) as f:
                data = json.load(f)
                for name in names:
                    if data[name]["dead"] == 1:
                        combo = f"{name}, **dead at {data[name]['age']}**"
                    else:
                        combo = f"{name},** {data[name]['age']}**"
                    combined.append(combo)
                combined.sort(
                    key=lambda x: int(x.rpartition(" ")[-1].strip("*")), reverse=True
                )
                content = "\n".join(combined)
                msg = discord.Embed(
                    title=self.title,
                    description=f"**__Contestants__**\n{content}",
                    color=color,
                    url=self.url,
                ).set_footer(text=f"Last updated {data['updated']}")
                await ctx.send(embed=msg)
        except Exception:
            ErrorLogger.run(traceback.format_exc())
            await ctx.send("Error logged in OPBR.")
