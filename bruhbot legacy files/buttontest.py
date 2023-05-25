import os

import discord as discord
from discord.ext import commands
from dotenv import load_dotenv

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="$", intents=intents)
load_dotenv(".\\bruhbot\\.env")
token = os.getenv("TOKEN")


class nView(discord.ui.View):
    async def disableb(self):
        for item in self.children:
            item.disabled = True
        await self.message.edit(view=self)
        await self.message.delete()

    @discord.ui.button(style=discord.ButtonStyle.danger, label="1")
    async def button1(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await self.ctx.send("Nerd")
        await self.disableb()

    @discord.ui.button(style=discord.ButtonStyle.danger, label="2")
    async def button2(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await self.ctx.send("Nerd")
        await self.disableb()

    @discord.ui.button(style=discord.ButtonStyle.danger, label="3")
    async def button3(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await self.ctx.send("Nerd")
        await self.disableb()

    @discord.ui.button(style=discord.ButtonStyle.danger, label="4")
    async def button4(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await self.ctx.send("Nerd")
        await self.disableb()

    @discord.ui.button(style=discord.ButtonStyle.danger, label="5")
    async def button5(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await self.ctx.send("Nerd")
        await self.disableb()

    @discord.ui.button(
        style=discord.ButtonStyle.blurple, emoji=discord.PartialEmoji.from_str("⏮️")
    )
    async def buttonfirst(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await self.ctx.send("Nerd")
        await self.disableb()

    @discord.ui.button(
        style=discord.ButtonStyle.blurple, emoji=discord.PartialEmoji.from_str("◀️")
    )
    async def buttonback(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await self.ctx.send("Nerd")
        await self.disableb()

    @discord.ui.button(
        style=discord.ButtonStyle.blurple, emoji=discord.PartialEmoji.from_str("▶️")
    )
    async def buttonnext(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await self.ctx.send("Nerd")
        await self.disableb()

    @discord.ui.button(
        style=discord.ButtonStyle.blurple, emoji=discord.PartialEmoji.from_str("⏭️")
    )
    async def buttonlast(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await self.ctx.send("Nerd")
        await self.disableb()

    @discord.ui.button(
        style=discord.ButtonStyle.secondary, emoji=discord.PartialEmoji.from_str("❌")
    )
    async def buttoncancel(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await self.ctx.send("Nerd")
        await self.disableb()


@bot.event
async def on_ready():
    print("Ready")


@bot.command()
async def button(ctx):
    msg = discord.Embed(title="Test", description="This is a test")
    view = nView()
    message = await ctx.send(embed=msg, view=view)
    view.message = message
    view.ctx = ctx
    await view.wait()


bot.run(token)
