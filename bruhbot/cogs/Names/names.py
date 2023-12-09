import json
import os
import random
import re
import traceback

import discord
from redbot.core import commands, app_commands

from bruhbot import ErrorLogger


class Names(commands.Cog):
    bot = commands.Bot(command_prefix="$", intents=discord.Intents.default())

    def __init__(self, bot):
        self.bot = bot
        self.file = f"{os.path.dirname(__file__)}\\names.json"

    async def get_color(self, ctx):
        if ctx.guild:
            color = ctx.guild.get_member(self.bot.user.id).top_role.color
            return color
        else:
            color = 0xE74C3C  # red
            return color

    @commands.hybrid_command(invoke_without_command=True)
    async def name(self, ctx):
        """
        The Random Name Generator.

        Generate a random name.
        """
        if ctx.invoked_subcommand is None:
            try:

                def roll():
                    with open(self.file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        name1 = random.choice(data["firstnames"])
                        name2 = random.choice(data["lastnames"])
                        name = f"{name1} {name2}"
                        emb = discord.Embed(
                            title="Your Character's Name Is:",
                            description=f"**{name}**",
                            color=color,
                        )
                        return emb

                class addModal(discord.ui.Modal, title="Add a new name"):
                    name1 = discord.ui.TextInput(
                        style=discord.TextStyle.short,
                        label="First name",
                        required=False,
                        placeholder="(Not required)",
                    )
                    name2 = discord.ui.TextInput(
                        style=discord.TextStyle.short,
                        label="Last name",
                        required=False,
                        placeholder="(Not required)",
                    )

                    async def on_submit(self, interaction: discord.Interaction):
                        await interaction.response.defer()
                        if (
                            re.sub("[^a-zA-Z]", "", str(self.name1)) == ""
                            and len(str(self.name1)) != 0
                            or re.sub("[^a-zA-z]", "", str(self.name2)) == ""
                            and len(str(self.name2)) != 0
                            or str(self.name1) == ""
                            and str(self.name2) == ""
                            or any(
                                char in (str(self.name1)) + str(self.name2)
                                for char in [":", "<", ">"]
                            )
                        ):
                            raise Exception
                        with open(self.file, "r+", encoding="utf-8") as f:
                            data = json.load(f)
                            if (
                                not str(self.name1) == ""
                                and str(self.name1) not in data["firstnames"]
                            ):
                                data["firstnames"].append(str(self.name1))
                            if (
                                not str(self.name2) == ""
                                and str(self.name2) not in data["lastnames"]
                            ):
                                data["lastnames"].append(str(self.name2))
                            f.seek(0)
                            json.dump(data, f, indent=4)
                            f.truncate()
                        await interaction.followup.send(
                            f'"{self.name1} {self.name2}" was added.',
                            ephemeral=True,
                        )

                    async def on_error(self, interaction: discord.Interaction, error):
                        await interaction.followup.send("Invalid Name.", ephemeral=True)

                class refreshView(discord.ui.View):
                    async def on_timeout(self) -> None:
                        await self.msg.edit(view=None)
                        self.stop()

                    async def check(self, interaction):
                        if interaction.user.id == ctx.author.id:
                            return True
                        else:
                            if self.counter < 5:
                                await interaction.followup.send(
                                    "That's not you button.", ephemeral=True
                                )
                                self.counter += 1
                            elif self.counter >= 5 and self.counter < 8:
                                await interaction.followup.send(
                                    "Dude stop.", ephemeral=True
                                )
                                self.counter += 1
                            else:
                                await interaction.followup.send(
                                    "Seriously dude, enough.", ephemeral=True
                                )

                    @discord.ui.button(
                        style=discord.ButtonStyle.secondary, label="Roll again"
                    )
                    async def buttonRefresh(
                        self,
                        interaction: discord.Interaction,
                        button: discord.ui.Button,
                    ):
                        await interaction.response.defer()
                        if await self.check(interaction) == True:
                            emb = roll()
                            await self.msg.edit(embed=emb, view=self)

                    @discord.ui.button(
                        style=discord.ButtonStyle.secondary, label="Add a new name"
                    )
                    async def buttonAdd(
                        self,
                        interaction: discord.Interaction,
                        button: discord.ui.Button,
                    ):
                        if await self.check(interaction) == True:
                            addM = addModal()
                            addM.file = self.file
                            await interaction.response.send_modal(addM)
                            await addM.wait()
                        else:
                            interaction.response.defer()

                color = await self.get_color(ctx)
                emb = roll()
                rview = refreshView(timeout=30)
                msg = await ctx.send(embed=emb, view=rview)
                rview.msg = msg
                rview.file = self.file
                rview.wait()
            except Exception:
                e = traceback.format_exc()
                ErrorLogger.run(e)
                await ctx.send("Error logged.")

    @app_commands.command(
        name="addname", description="Add a name to the name generator."
    )
    async def addname(self, interaction: discord.Interaction):
        try:

            class addModal(discord.ui.Modal, title="Add a new name"):
                name1 = discord.ui.TextInput(
                    style=discord.TextStyle.short,
                    label="First name",
                    required=False,
                    placeholder="(Not required)",
                )
                name2 = discord.ui.TextInput(
                    style=discord.TextStyle.short,
                    label="Last name",
                    required=False,
                    placeholder="(Not required)",
                )
                file = f"{os.path.dirname(__file__)}\\names.json"

                async def on_submit(self, interaction: discord.Interaction):
                    await interaction.response.defer()
                    if (
                        re.sub("[^a-zA-Z]", "", str(self.name1)) == ""
                        and len(str(self.name1)) != 0
                        or re.sub("[^a-zA-z]", "", str(self.name2)) == ""
                        and len(str(self.name2)) != 0
                        or str(self.name1) == ""
                        and str(self.name2) == ""
                        or any(
                            char in (str(self.name1)) + str(self.name2)
                            for char in [":", "<", ">"]
                        )
                    ):
                        raise Exception
                    with open(self.file, "r+", encoding="utf-8") as f:
                        data = json.load(f)
                        if (
                            not str(self.name1) == ""
                            and str(self.name1) not in data["firstnames"]
                        ):
                            data["firstnames"].append(str(self.name1))
                        if (
                            not str(self.name2) == ""
                            and str(self.name2) not in data["lastnames"]
                        ):
                            data["lastnames"].append(str(self.name2))
                        f.seek(0)
                        json.dump(data, f, indent=4)
                        f.truncate()
                    await interaction.followup.send(
                        f'"{self.name1} {self.name2}" was added.',
                        ephemeral=True,
                    )

                async def on_error(self, interaction: discord.Interaction, error):
                    await interaction.followup.send("Invalid Name.", ephemeral=True)
                    ErrorLogger.run(error)

            addM = addModal()
            await interaction.response.send_modal(addM)
            await addM.wait()
        except Exception:
            e = traceback.format_exc()
            ErrorLogger.run(e)
            await interaction.followup.send("Error logged.")
