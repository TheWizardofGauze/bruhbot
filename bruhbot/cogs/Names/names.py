import json
import os
from random import choice, random
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
        color = ctx.guild.get_member(self.bot.user.id).top_role.color if ctx.guild else 0xE74C3C  # red
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
                        name1 = choice(data["firstnames"])
                        name2 = choice(data["lastnames"])
                        prefix = choice(data["prefix"]) if random() < 0.05 else ""
                        suffix = choice(data["suffix"]) if random() < 0.05 else ""
                        name = f"{prefix} {name1} {name2} {suffix}".strip()
                        emb = discord.Embed(
                            title="Your Character's Name Is:",
                            description=f"**{name}**",
                            color=color,
                        )
                        return emb

                class addModal(discord.ui.Modal, title="Add a new name"):
                    prefix = discord.ui.TextInput(
                        style=discord.TextStyle.short,
                        label="Title/Prefix",
                        required=False,
                        placeholder="(Not required)",
                    )
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
                    suffix = discord.ui.TextInput(
                        style=discord.TextStyle.short,
                        label="Suffix",
                        required=False,
                        placeholder="(Not required)",
                    )

                    async def on_submit(self, interaction: discord.Interaction):
                        await interaction.response.defer()
                        if any(
                            re.sub("[^a-zA-Z]", "", str(name)) == "" and len(str(name)) != 0
                            for name in [self.prefix, self.name1, self.name2, self.suffix]
                        ) or all(name == "" for name in [self.prefix, self.name1, self.name2, self.suffix]):
                            await interaction.followup.send("Invalid Name.", ephemeral=True)
                            raise Exception
                        with open(self.file, "r+", encoding="utf-8") as f:
                            data = json.load(f)
                            if not str(self.prefix) == "" and str(self.prefix) not in data["prefix"]:
                                data["prefix"].append(str(self.prefix))
                            if not str(self.name1) == "" and str(self.name1) not in data["firstnames"]:
                                data["firstnames"].append(str(self.name1))
                            if not str(self.name2) == "" and str(self.name2) not in data["lastnames"]:
                                data["lastnames"].append(str(self.name2))
                            if not str(self.suffix) == "" and str(self.suffix) not in data["suffix"]:
                                data["suffix"].append(str(self.suffix))
                            f.seek(0)
                            json.dump(data, f, indent=4)
                            f.truncate()
                        await interaction.followup.send(
                            f'"{f"{self.prefix} {self.name1} {self.name2} {self.suffix}".strip()}" was added.',
                            ephemeral=True,
                        )

                    # async def on_error(self, interaction: discord.Interaction):
                    #     await interaction.followup.send("Invalid Name.", ephemeral=True)

                class refreshView(discord.ui.View):
                    async def on_timeout(self) -> None:
                        await self.msg.edit(view=None)
                        self.stop()

                    async def check(self, interaction: discord.Interaction):
                        if interaction.user.id == ctx.author.id:
                            return True
                        else:
                            if self.counter < 5:
                                await interaction.followup.send("That's not your button.", ephemeral=True)
                                self.counter += 1
                            elif self.counter >= 5 and self.counter < 8:
                                await interaction.followup.send("Dude stop.", ephemeral=True)
                                self.counter += 1
                            else:
                                await interaction.followup.send("Seriously dude, enough.", ephemeral=True)

                    @discord.ui.button(style=discord.ButtonStyle.secondary, label="Roll again")
                    async def buttonRefresh(
                        self,
                        interaction: discord.Interaction,
                        button: discord.ui.Button,
                    ):
                        await interaction.response.defer()
                        if await self.check(interaction) is True:
                            emb = roll()
                            await self.msg.edit(embed=emb, view=self)

                    @discord.ui.button(style=discord.ButtonStyle.secondary, label="Add a new name")
                    async def buttonAdd(
                        self,
                        interaction: discord.Interaction,
                        button: discord.ui.Button,
                    ):
                        if await self.check(interaction) is True:
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
                ErrorLogger.run(traceback.format_exc())
                await ctx.send("Error logged in Names.")

    @app_commands.command(name="addname", description="Add a name to the name generator.")
    async def addname(self, interaction: discord.Interaction):
        try:

            class addModal(discord.ui.Modal, title="Add a new name"):
                prefix = discord.ui.TextInput(
                    style=discord.TextStyle.short,
                    label="Title/Prefix",
                    required=False,
                    placeholder="(Not required)",
                )
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
                suffix = discord.ui.TextInput(
                    style=discord.TextStyle.short,
                    label="Suffix",
                    required=False,
                    placeholder="(Not required)",
                )
                file = f"{os.path.dirname(__file__)}\\names.json"

                async def on_submit(self, interaction: discord.Interaction):
                    await interaction.response.defer()
                    if any(
                        re.sub("[^a-zA-Z]", "", str(name)) == "" and len(str(name)) != 0
                        for name in [self.prefix, self.name1, self.name2, self.suffix]
                    ) or all(name == "" for name in [self.prefix, self.name1, self.name2, self.suffix]):
                        await interaction.followup.send("Invalid Name.", ephemeral=True)
                        raise Exception
                    with open(self.file, "r+", encoding="utf-8") as f:
                        data = json.load(f)
                        if not str(self.prefix) == "" and str(self.prefix) not in data["prefix"]:
                            data["prefix"].append(str(self.prefix))
                        if not str(self.name1) == "" and str(self.name1) not in data["firstnames"]:
                            data["firstnames"].append(str(self.name1))
                        if not str(self.name2) == "" and str(self.name2) not in data["lastnames"]:
                            data["lastnames"].append(str(self.name2))
                        if not str(self.suffix) == "" and str(self.suffix) not in data["suffix"]:
                            data["suffix"].append(str(self.suffix))
                        f.seek(0)
                        json.dump(data, f, indent=4)
                        f.truncate()
                    await interaction.followup.send(
                        f'"{f"{self.prefix} {self.name1} {self.name2} {self.suffix}".strip()}" was added.',
                        ephemeral=True,
                    )

                # async def on_error(self, interaction: discord.Interaction):
                #     await interaction.followup.send("Invalid Name.", ephemeral=True)

            addM = addModal()
            await interaction.response.send_modal(addM)
            await addM.wait()
        except Exception:
            ErrorLogger.run(traceback.format_exc())
            await interaction.followup.send("Error logged in Names.")
