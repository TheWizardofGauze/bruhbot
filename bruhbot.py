import asyncio
from contextlib import suppress
from datetime import date, datetime
from io import BytesIO
import json
import os
from random import choice, random
import re
import string
import traceback

from dateutil.relativedelta import relativedelta
import discord
from discord.ext import commands
from discord.utils import escape_markdown
from dotenv import load_dotenv

from bruhbot import ResponseBackup, ErrorLogger, ForzaSeason


intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="$", intents=intents)
bot.remove_command("help")
load_dotenv(".\\bruhbot\\.env")
token = os.getenv("TOKEN")
owner_id = int(os.getenv("OWNER_ID"))
ignored_channel = int(os.getenv("IGNORED_CHANNEL"))
here = os.path.dirname(__file__)


async def check_age():
    def plural(num: int):
        return 0 if num == 1 else 1

    while True:
        now = date.today()
        bday = date(2020, 6, 20)
        rdelta = relativedelta(now, bday)
        year = ["year", "years"]
        if rdelta.months == 0 and rdelta.days == 0:
            await bot.change_presence(
                activity=discord.CustomActivity(
                    name=f"Been a stinky dingus for {rdelta.years} {year[plural(rdelta.years)]}",
                    emoji=discord.PartialEmoji.from_str("🎂"),
                )
            )
        else:
            await bot.change_presence(status=discord.Status.online)
        await asyncio.sleep(3600)


async def auto_backup():
    try:
        with open(f"{here}\\bruhbot\\data.json", "r+") as f:
            data = json.load(f)
            now = date.today()
            last = datetime.strptime(data["lastbackup"], "%Y-%m-%d")
            rdelta = relativedelta(now, last)
            if rdelta.months >= 1:
                ResponseBackup.run()
                data["lastbackup"] = now.strftime("%Y-%m-%d")
                f.seek(0)
                json.dump(data, f, indent=4)
            else:
                return
    except Exception:
        owner = await bot.fetch_user(owner_id)
        await owner.send("Error logged in auto backup.")
        ErrorLogger.run(traceback.format_exc())
        return


async def get_color(ctx):
    color = ctx.guild.get_member(bot.user.id).top_role.color if ctx.guild else 0xE74C3C  # red
    return color


async def send_image(ctx, response: str, suppress: bool):
    try:
        image = response.replace(" - image", "")
        await ctx.reply(file=discord.File(f"{here}\\images\\{image}"), mention_author=False)
    except Exception:  # missing image
        if suppress is False:
            await ctx.reply("Error logged in send_image.")
            ErrorLogger.run(traceback.format_exc())
            return
        else:
            return


@bot.event
async def on_ready():
    servers = list(bot.guilds)
    print(f"{bot.user.name}(ID:{bot.user.id}) connected to {str(len(servers))} servers")
    await auto_backup()
    await check_age()


@bot.event
async def on_message(msg):
    try:
        await bot.process_commands(msg)
        ctx = await bot.get_context(msg)
        if ctx.author.bot or ctx.channel.id == ignored_channel:
            return
        nospace = re.sub("[^a-zA-Z0-9]", "", msg.content).lower()
        name = re.sub("[^a-zA-Z0-9]", "", ctx.me.display_name).lower()
        top_role = str(ctx.guild.get_member(bot.user.id).top_role.id) if ctx.guild else None

        if (
            name in nospace
            or top_role is not None
            and top_role in nospace
            or bot.user in msg.mentions
            or (
                msg.reference is not None
                and msg.reference.resolved is not None
                and msg.reference.resolved.author == bot.user
            )
        ):
            async with ctx.typing():
                if random() < 0.005:
                    await ctx.reply(ctx.author.display_avatar, mention_author=False)
                    return
                responses = []
                with open(f"{here}\\bruhbot\\responses.txt", "r", encoding="utf-8") as f:
                    for line in f:
                        current = line[:-1]
                        responses.append(current)
                response = choice(responses).replace(r"\n", "\n")
                if response.endswith("- image"):
                    await send_image(ctx, response, False)
                    return
                await ctx.reply(response, mention_author=False)
                return
        if "69" in nospace:
            await ctx.reply("nice", mention_author=False)  # nice
            return
        if "420" in nospace:
            await ctx.reply("weed", mention_author=False)  # weed
            return
    except Exception:
        await ctx.reply("Error logged in on_message.")
        ErrorLogger.run(traceback.format_exc())


@bot.command()
async def addr(ctx, *, arg: str = None):
    try:
        if ctx.message.attachments or ctx.message.reference:  # image support
            if ctx.message.reference:
                attachments = ctx.message.reference.resolved.attachments
            else:
                attachments = ctx.message.attachments
            invalid_counter = 0
            size_counter = 0
            dupe_counter = 0
            filesize_limit = 26214400
            for attachment in attachments:
                dupe = False
                if "image" in attachment.content_type:
                    if attachment.size > filesize_limit:
                        if len(attachments) == 1:
                            await ctx.reply("Error: File too large. (Max 25MB)")
                            return
                        else:
                            size_counter += 1
                    ext = os.path.splitext(attachment.filename)[-1]
                    with open(f"{here}\\bruhbot\\responses.txt", "r", encoding="utf-8") as f:
                        if arg and len(attachments) == 1:
                            pre = os.path.splitext("".join(arg[:]))[0] + ext
                        else:
                            if (
                                attachment.filename == f"image0{ext}"
                                or attachment.filename == f"unknown{ext}"
                                or attachment.filename == f"image{ext}"
                            ):
                                new = "".join(choice(string.ascii_letters + string.digits) for i in range(6))
                                while os.path.exists(f".\\images\\{new}"):
                                    new = new + "".join(choice(string.digits))
                                pre = new + ext
                            else:
                                pre = attachment.filename
                        file = f.readlines()
                        for line in file:
                            if pre.lower() == line.lower().replace(" - image\n", ""):
                                if len(attachments) == 1:
                                    await ctx.reply(f"Error: **'{pre}'** already exists:")
                                    return
                                else:
                                    dupe_counter += 1
                                    dupe = True
                                    break
                    if dupe is False:
                        async with ctx.typing():
                            await attachment.save(f"{here}\\images\\{pre}")
                    else:
                        continue
                    with open(f"{here}\\bruhbot\\responses.txt", "a", encoding="utf-8") as f:
                        f.write(f"{pre} - image\n")
                else:
                    if len(attachments) == 1:
                        await ctx.reply("Error: Invalid file type.")
                        return
                    else:
                        invalid_counter += 1
            if (
                len(attachments) - invalid_counter == 1
                or len(attachments) - dupe_counter == 1
                or len(attachments) - size_counter == 1
            ):
                added = "Image was added."
            elif (
                len(attachments) - invalid_counter == 0
                or len(attachments) - dupe_counter == 0
                or len(attachments) - size_counter == 0
            ):
                added = "No images were added."
            else:
                added = "Images were added."
            if not invalid_counter == len(attachments):
                await ctx.reply(f"{added} :thumbsup:", mention_author=False)
            if dupe_counter > 0:
                await ctx.send(f"Blocked {str(dupe_counter)} duplicate files.")
            if invalid_counter > 0:
                await ctx.send(f"Blocked {str(invalid_counter)} invalid files.")
            if size_counter > 0:
                await ctx.send(f"Blocked {str(size_counter)} large files. (Max 25MB)")
            return
        if not arg and not ctx.message.reference:
            await help(ctx, "addr")
            return
        with open(f"{here}\\bruhbot\\responses.txt", "r", encoding="utf-8") as f:
            pre1 = "".join(arg[:])
            pre = pre1.replace("\n", r"\n")
            file = f.readlines()
            for line in file:
                if pre.lower() == line.lower().strip("\n"):
                    await ctx.reply("Error: Response already exists.")
                    return
        with open(f"{here}\\bruhbot\\responses.txt", "a", encoding="utf-8") as f:
            f.write(pre + "\n")
        await ctx.reply(f"**'{pre1}'** was added. :thumbsup:", mention_author=False)
    except Exception:
        await ctx.reply("Error logged in addr.")
        ErrorLogger.run(traceback.format_exc())


@bot.command()
async def delr(ctx, *arg: str):
    try:

        def get_list(responses: list, start: int, end: int, curPage: int):
            numbered = []
            for i, j in enumerate(responses[start:end], 1):
                if len(j) > 400:
                    j = j[:404] + "..."
                j = escape_markdown(str(i) + ": " + j)
                numbered.append(j)
            content = "\n".join(numbered)
            emb = discord.Embed(
                title="Delete response",
                description=f"**Page {curPage}/{pages}:**\n{content}",
                color=color,
            )
            return emb

        class pageModal(discord.ui.Modal, title="Enter a page number"):
            page = discord.ui.TextInput(
                style=discord.TextStyle.short,
                label="Page",
                required=True,
                placeholder="Enter a page number",
            )

            async def on_submit(self, interaction: discord.Interaction):
                await interaction.response.defer()
                if not int(self.page.value):
                    raise Exception

            async def on_error(self, interaction: discord.Interaction):
                await interaction.followup.send("Error: Page must be a number.", ephemeral=True)

        class menuView(discord.ui.View):
            async def on_timeout(self) -> None:
                emb = discord.Embed(title="Timeout", description="", color=color)
                await self.msg.edit(embed=emb, view=None)
                self.timeout = True
                self.stop()

            async def update(self):
                if self.curPage == 1:
                    self.buttonBack10.disabled = True
                    self.buttonBack.disabled = True
                else:
                    self.buttonBack10.disabled = False
                    self.buttonBack.disabled = False
                if self.curPage == self.pages:
                    self.buttonNext.disabled = True
                    self.buttonNext10.disabled = True
                else:
                    self.buttonNext.disabled = False
                    self.buttonNext10.disabled = False
                if len(responses[self.start : self.end]) < 5:
                    self.button5.disabled = True
                    if len(responses[self.start : self.end]) < 4:
                        self.button4.disabled = True
                        if len(responses[self.start : self.end]) < 3:
                            self.button3.disabled = True
                            if len(responses[self.start : self.end]) < 2:
                                self.button2.disabled = True
                else:
                    self.button1.disabled = False
                    self.button2.disabled = False
                    self.button3.disabled = False
                    self.button4.disabled = False
                    self.button5.disabled = False

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

            counter: int = 0
            choice: int = None
            cancel: bool = None

            @discord.ui.button(style=discord.ButtonStyle.danger, label="1")
            async def button1(self, interaction: discord.Interaction, button: discord.ui.Button):
                await interaction.response.defer()
                if await self.check(interaction) is True:
                    self.choice = 0
                    await self.msg.delete()
                    self.stop()

            @discord.ui.button(style=discord.ButtonStyle.danger, label="2")
            async def button2(self, interaction: discord.Interaction, button: discord.ui.Button):
                await interaction.response.defer()
                if await self.check(interaction) is True:
                    self.choice = 1
                    await self.msg.delete()
                    self.stop()

            @discord.ui.button(style=discord.ButtonStyle.danger, label="3")
            async def button3(self, interaction: discord.Interaction, button: discord.ui.Button):
                await interaction.response.defer()
                if await self.check(interaction) is True:
                    self.choice = 2
                    await self.msg.delete()
                    self.stop()

            @discord.ui.button(style=discord.ButtonStyle.danger, label="4")
            async def button4(self, interaction: discord.Interaction, button: discord.ui.Button):
                await interaction.response.defer()
                if await self.check(interaction) is True:
                    self.choice = 3
                    await self.msg.delete()
                    self.stop()

            @discord.ui.button(style=discord.ButtonStyle.danger, label="5")
            async def button5(self, interaction: discord.Interaction, button: discord.ui.Button):
                await interaction.response.defer()
                if await self.check(interaction) is True:
                    self.choice = 4
                    await self.msg.delete()
                    self.stop()

            @discord.ui.button(
                style=discord.ButtonStyle.blurple,
                emoji=discord.PartialEmoji.from_str("⏪"),
            )
            async def buttonBack10(self, interaction: discord.Interaction, button: discord.ui.Button):
                await interaction.response.defer()
                if await self.check(interaction) is True:
                    self.curPage = max(1, self.curPage - 10)
                    self.start = max(0, self.start - 50)
                    self.end = max(5, self.end - 50)
                    emb = get_list(responses, self.start, self.end, self.curPage)
                    await self.update()
                    await self.msg.edit(embed=emb, view=self)

            @discord.ui.button(
                style=discord.ButtonStyle.blurple,
                emoji=discord.PartialEmoji.from_str("◀️"),
            )
            async def buttonBack(self, interaction: discord.Interaction, button: discord.ui.Button):
                await interaction.response.defer()
                if await self.check(interaction) is True:
                    self.curPage -= 1
                    self.start -= 5
                    self.end -= 5
                    emb = get_list(responses, self.start, self.end, self.curPage)
                    await self.update()
                    await self.msg.edit(embed=emb, view=self)

            @discord.ui.button(
                style=discord.ButtonStyle.blurple,
                emoji=discord.PartialEmoji.from_str("▶️"),
            )
            async def buttonNext(self, interaction: discord.Interaction, button: discord.ui.Button):
                await interaction.response.defer()
                if await self.check(interaction) is True:
                    self.curPage += 1
                    self.start += 5
                    self.end += 5
                    emb = get_list(responses, self.start, self.end, self.curPage)
                    await self.update()
                    await self.msg.edit(embed=emb, view=self)

            @discord.ui.button(
                style=discord.ButtonStyle.blurple,
                emoji=discord.PartialEmoji.from_str("⏩"),
            )
            async def buttonNext10(self, interaction: discord.Interaction, button: discord.ui.Button):
                await interaction.response.defer()
                if await self.check(interaction) is True:
                    self.curPage = min(self.pages, self.curPage + 10)
                    self.start = min(self.pages * 5 - 5, self.start + 50)
                    self.end = min(self.pages * 5, self.end + 50)
                    emb = get_list(responses, self.start, self.end, self.curPage)
                    await self.update()
                    await self.msg.edit(embed=emb, view=self)

            @discord.ui.button(
                style=discord.ButtonStyle.secondary,
                emoji=discord.PartialEmoji.from_str("📖"),
            )
            async def buttonPage(self, interaction: discord.Interaction, button: discord.ui.Button):
                if await self.check(interaction) is True:
                    pageM = pageModal()
                    await interaction.response.send_modal(pageM)
                    await pageM.wait()
                    page = int(pageM.page.value)
                    if page > self.pages:
                        self.curPage = min(self.pages, page)
                        self.start = min(self.pages, page) * 5 - 5
                        self.end = min(self.pages, page) * 5
                    elif page < 1:
                        self.curPage = 1
                        self.start = 0
                        self.end = 5
                    else:
                        self.curPage = page
                        self.start = page * 5 - 5
                        self.end = page * 5
                    emb = get_list(responses, self.start, self.end, self.curPage)
                    await self.update()
                    await self.msg.edit(embed=emb, view=self)
                else:
                    await interaction.response.defer()

            @discord.ui.button(
                style=discord.ButtonStyle.secondary,
                emoji=discord.PartialEmoji.from_str("❌"),
            )
            async def buttonCancel(self, interaction: discord.Interaction, button: discord.ui.Button):
                await interaction.response.defer()
                if await self.check(interaction) is True:
                    self.cancel = True
                    emb = discord.Embed(title="Canceled", description="", color=color)
                    await self.msg.edit(embed=emb, view=None)
                    self.stop()

        class confirmView(discord.ui.View):
            async def on_timeout(self) -> None:
                emb = discord.Embed(title="Timeout", description="", color=color)
                await self.msg.edit(embed=emb, view=None)
                self.timeout = True
                self.stop()

            async def check(self, interaction: discord.Interaction):
                if interaction.user.id == ctx.author.id:
                    return True
                else:
                    await interaction.followup.send("That's not your button.", ephemeral=True)

            confirm: bool = None
            cancel: bool = None

            @discord.ui.button(style=discord.ButtonStyle.success, label="Confirm")
            async def buttonConfirm(self, interaction: discord.Interaction, button: discord.ui.Button):
                await interaction.response.defer()
                if await self.check(interaction) is True:
                    self.confirm = True
                    await self.msg.delete()
                    self.stop()

            @discord.ui.button(style=discord.ButtonStyle.danger, label="Cancel")
            async def buttonCancel(self, interaction: discord.Interaction, button: discord.ui.Button):
                await interaction.response.defer()
                if await self.check(interaction) is True:
                    self.cancel = True
                    emb = discord.Embed(title="Canceled", description="", color=color)
                    await self.msg.edit(embed=emb, view=None)
                    self.stop()

        start = 0
        end = 5
        pages = 0
        curPage = 1
        responses = []
        color = await get_color(ctx)
        with open(f"{here}\\bruhbot\\responses.txt", "r", encoding="utf-8") as f:
            file = f.readlines()
            for line in file:
                current = line[:-1]
                responses.append(current)
        if arg:  # direct
            try:
                choice = int("".join(arg[:])) - 1
                if choice + 1 <= 0 or choice + 1 > len(responses):
                    raise IndexError
            except ValueError:
                await ctx.reply("Selection must be a number.")
                return
            except IndexError:
                await ctx.reply("Error: Selection out of range.")
                return
            async with ctx.typing():
                if responses[choice].endswith("- image"):
                    await send_image(ctx, responses[choice], True)
                    item = "image?"
                else:
                    item = f"response?: \n**{responses[choice]}**"
                emb = discord.Embed(
                    title="Delete response",
                    description=f"Are you sure you want to delete this {item}",
                    color=color,
                )
            cview = confirmView(timeout=10)
            msg = await ctx.send(embed=emb, view=cview)
            cview.msg = msg
            await cview.wait()
            if cview.confirm is True:
                with open(f"{here}\\bruhbot\\responses.txt", "w", encoding="utf-8") as f:
                    for line in file:
                        if line.strip("\n").lower() != responses[choice].lower():
                            f.write(line)
                if " - image" in responses[choice]:
                    with suppress(FileNotFoundError):
                        image = responses[choice].replace(" - image", "")
                        name = image
                        os.remove(f"{here}\\images\\{image}")
                else:
                    name = responses[choice]
                await ctx.reply(f"**'{name}'** was deleted. :thumbsup:", mention_author=False)
                return
            if cview.cancel is True or cview.timeout is True:
                return
        if not arg:  # menu
            mview = menuView(timeout=30)
            while pages < len(responses) / 5:
                pages += 1
            emb = get_list(responses, start, end, curPage)
            mview.start = start
            mview.end = end
            mview.pages = pages
            mview.curPage = curPage
            mview.responses = responses
            await mview.update()
            msg = await ctx.send(embed=emb, view=mview)
            mview.msg = msg
            await mview.wait()
            if mview.cancel is True or mview.timeout is True:
                return
            if mview.choice is not None:
                if mview.choice + 1 > len(responses[mview.start : mview.end]):
                    await ctx.reply("Invalid selection. That shouldn't happen...")
                    raise Exception
                async with ctx.typing():
                    if responses[mview.start : mview.end][mview.choice].endswith("- image"):
                        await send_image(ctx, responses[mview.start : mview.end][mview.choice], True)
                        item = "image"
                    else:
                        item = f"response?: \n**{responses[mview.start : mview.end][mview.choice]}**"
                    emb = discord.Embed(
                        title="Delete response",
                        description=f"Are you sure you want to delete this {item}",
                        color=color,
                    )
                cview = confirmView(timeout=10)
                msg = await ctx.send(embed=emb, view=cview)
                cview.msg = msg
                await cview.wait()
                if cview.confirm is True:
                    with open(f"{here}\\bruhbot\\responses.txt", "w", encoding="utf-8") as f:
                        for line in file:
                            if line.strip("\n").lower() != responses[mview.start : mview.end][mview.choice].lower():
                                f.write(line)
                    if " - image" in responses[mview.start : mview.end][mview.choice]:
                        with suppress(FileNotFoundError):
                            image = responses[mview.start : mview.end][mview.choice].replace(" - image", "")
                            name = image
                            os.remove(f"{here}\\images\\{image}")
                    else:
                        name = responses[mview.start : mview.end][mview.choice]
                    await ctx.reply(
                        f"**'{name}'** was deleted. :thumbsup:",
                        mention_author=False,
                    )
                if cview.cancel is True or cview.timeout is True:
                    return

    except Exception:
        await ctx.reply("Error logged in delr.")
        ErrorLogger.run(traceback.format_exc())


@bot.command()
async def rlist(ctx):
    try:

        def get_list(numbered: list, start: int, end: int, curPage: int):
            content = "\n".join(numbered[start:end])
            emb = discord.Embed(
                title="Response list",
                description=f"**Page {curPage}/{pages}:**\n{content}",
                color=color,
            )
            return emb

        class pageModal(discord.ui.Modal, title="Enter a page number"):
            page = discord.ui.TextInput(
                style=discord.TextStyle.short,
                label="Page",
                required=True,
                placeholder="Enter a page number",
            )

            async def on_submit(self, interaction: discord.Interaction):
                await interaction.response.defer()
                if not int(self.page.value):
                    raise Exception

            async def on_error(self, interaction: discord.Interaction):
                await interaction.followup.send("Error: Page must be a number.", ephemeral=True)

        class menuView(discord.ui.View):
            async def on_timeout(self) -> None:
                await self.msg.delete()
                self.timeout = True
                self.stop()

            async def update(self):
                if self.curPage == 1:
                    self.buttonBack10.disabled = True
                    self.buttonBack.disabled = True
                else:
                    self.buttonBack10.disabled = False
                    self.buttonBack.disabled = False
                if self.curPage == self.pages:
                    self.buttonNext.disabled = True
                    self.buttonNext10.disabled = True
                else:
                    self.buttonNext.disabled = False
                    self.buttonNext10.disabled = False

            async def check(self, interaction: discord.Interaction):
                if interaction.user.id == ctx.author.id:
                    return True
                else:
                    if self.counter < 5:
                        await interaction.followup.send("That's not you button.", ephemeral=True)
                        self.counter += 1
                    elif self.counter >= 5 and self.counter < 8:
                        await interaction.followup.send("Dude stop.", ephemeral=True)
                        self.counter += 1
                    else:
                        await interaction.followup.send("Seriously dude, enough.", ephemeral=True)

            counter: int = 0

            @discord.ui.button(
                style=discord.ButtonStyle.blurple,
                emoji=discord.PartialEmoji.from_str("⏪"),
            )
            async def buttonBack10(self, interaction: discord.Interaction, button: discord.ui.Button):
                await interaction.response.defer()
                if await self.check(interaction) is True:
                    self.curPage = max(1, self.curPage - 10)
                    self.start = max(0, self.start - 250)
                    self.end = max(25, self.end - 250)
                    emb = get_list(numbered, self.start, self.end, self.curPage)
                    await self.update()
                    await self.msg.edit(embed=emb, view=self)

            @discord.ui.button(
                style=discord.ButtonStyle.blurple,
                emoji=discord.PartialEmoji.from_str("◀️"),
            )
            async def buttonBack(self, interaction: discord.Interaction, button: discord.ui.Button):
                await interaction.response.defer()
                if await self.check(interaction) is True:
                    self.curPage -= 1
                    self.start -= 25
                    self.end -= 25
                    emb = get_list(numbered, self.start, self.end, self.curPage)
                    await self.update()
                    await self.msg.edit(embed=emb, view=self)

            @discord.ui.button(
                style=discord.ButtonStyle.blurple,
                emoji=discord.PartialEmoji.from_str("▶️"),
            )
            async def buttonNext(self, interaction: discord.Interaction, button: discord.ui.Button):
                await interaction.response.defer()
                if await self.check(interaction) is True:
                    self.curPage += 1
                    self.start += 25
                    self.end += 25
                    emb = get_list(numbered, self.start, self.end, self.curPage)
                    await self.update()
                    await self.msg.edit(embed=emb, view=self)

            @discord.ui.button(
                style=discord.ButtonStyle.blurple,
                emoji=discord.PartialEmoji.from_str("⏩"),
            )
            async def buttonNext10(self, interaction: discord.Interaction, button: discord.ui.Button):
                await interaction.response.defer()
                if await self.check(interaction) is True:
                    self.curPage = min(self.pages, self.curPage + 10)
                    self.start = min(self.pages * 25 - 25, self.start + 250)
                    self.end = min(self.pages * 25, self.end + 250)
                    emb = get_list(numbered, self.start, self.end, self.curPage)
                    await self.update()
                    await self.msg.edit(embed=emb, view=self)

            @discord.ui.button(
                style=discord.ButtonStyle.secondary,
                emoji=discord.PartialEmoji.from_str("📖"),
            )
            async def buttonPage(self, interaction: discord.Interaction, button: discord.ui.Button):
                if await self.check(interaction) is True:
                    pageM = pageModal()
                    await interaction.response.send_modal(pageM)
                    await pageM.wait()
                    page = int(pageM.page.value)
                    if page > self.pages:
                        self.curPage = min(self.pages, page)
                        self.start = min(self.pages, page) * 25 - 25
                        self.end = min(self.pages, page) * 25
                    elif page < 1:
                        self.curPage = 1
                        self.start = 0
                        self.end = 25
                    else:
                        self.curPage = page
                        self.start = page * 25 - 25
                        self.end = page * 25
                    emb = get_list(numbered, self.start, self.end, self.curPage)
                    await self.update()
                    await self.msg.edit(embed=emb, view=self)
                else:
                    interaction.response.defer()

        start = 0
        end = 25
        pages = 0
        curPage = 1
        responses = []
        numbered = []
        color = await get_color(ctx)
        with open(f"{here}\\bruhbot\\responses.txt", "r", encoding="utf-8") as f:
            file = f.readlines()
            for line in file:
                current = line[:-1]
                responses.append(current)
        for i, j in enumerate(responses, 1):  # character limit fix
            if len(j) > 81:
                j = j[:73] + "..."
            j = escape_markdown(str(i) + ": " + j)
            numbered.append(j)
        while pages < len(responses) / 25:
            pages += 1
        emb = get_list(numbered, start, end, curPage)
        mview = menuView(timeout=30)
        mview.start = start
        mview.end = end
        mview.pages = pages
        mview.curPage = curPage
        await mview.update()
        msg = await ctx.reply(embed=emb, view=mview, mention_author=False)
        mview.msg = msg
        await mview.wait()
    except Exception:
        await ctx.reply("Error logged rlist.")
        ErrorLogger.run(traceback.format_exc())


@bot.command()
@commands.is_owner()
async def rtest(ctx, arg: str):  # for testing responses
    try:
        choice = int(arg) - 1
    except ValueError:
        return
    responses = []
    with open(f"{here}\\bruhbot\\responses.txt", "r", encoding="utf-8") as f:
        for line in f:
            current = line[:-1]
            responses.append(current)
    if choice + 1 > len(responses) or choice < 0:
        await ctx.reply("Error: Selection out of range.")
        return
    response = responses[choice].replace(r"\n", "\n")
    if response.endswith("- image"):
        await send_image(ctx, response, False)
        return
    await ctx.reply(response, mention_author=False)


@bot.command()
async def help(ctx, *arg: str):
    try:

        def embed(ctx, name: str, description: str, color: int, pages: int):
            embed = discord.Embed(color=color)
            if pages > 1:
                embed.title = "*Bruhbot*"
                for page in range(pages):
                    embed.add_field(name=name[page], value=description[page], inline=False)
            else:
                embed.description = description
            embed.set_author(
                name=f"{ctx.me.display_name} Help Menu",
                icon_url=bot.user.display_avatar,
            )
            embed.set_footer(
                text="Type $help <command> for more info on a command. You can also type $help <category> for more info on a category."
            )
            return embed

        pre = " ".join(arg[:]).lower()
        args = ["addr", "delr", "rlist", "age", "forza", "response", "extra"]
        helpColor = await get_color(ctx)
        if pre in args:
            with open(f"{here}\\bruhbot\\data.json") as f:
                data = json.load(f)
                helpDes = data[pre]["description"]
            msg = embed(ctx, None, helpDes, helpColor, 1)
            await ctx.send(embed=msg)
        elif not arg:
            categories = ["response", "extra"]
            helpName = []
            helpDes = []
            with open(f"{here}\\bruhbot\\data.json") as f:
                data = json.load(f)
                for cat in categories:
                    helpDes.append(data[cat]["description"])
                    helpName.append(data[cat]["name"])
                msg = embed(
                    ctx,
                    helpName,
                    helpDes,
                    helpColor,
                    len(categories),
                )
                await ctx.send(embed=msg)
        else:
            return
    except Exception:
        await ctx.reply("Error logged in help.")
        ErrorLogger.run(traceback.format_exc())


@bot.command()
async def age(ctx):
    def plural(num: int):
        return 0 if num == 1 else 1

    now = date.today()
    bday = date(2020, 6, 20)
    rdelta = relativedelta(now, bday)
    plurals = [["year", "years"], ["month", "months"], ["day", "days"]]
    await ctx.reply(
        f"I am {rdelta.years} {plurals[0][plural(rdelta.years)]}, {rdelta.months} {plurals[1][plural(rdelta.months)]}, {rdelta.days} {plurals[2][plural(rdelta.days)]} old.",
        mention_author=False,
    )


@bot.group(invoke_without_command=True, ignore_extra=False)
async def forza(ctx):
    if ctx.invoked_subcommand is None:
        season = ForzaSeason.season()
        await ctx.reply(
            f"Horizon 4: {season[0].capitalize()}\nHorizon 5: {season[1].capitalize()}",
            mention_author=False,
        )


@forza.error
async def forza_error(ctx, error):
    if isinstance(error, commands.errors.TooManyArguments):
        await help(ctx, "forza")
    else:
        await ctx.reply("Error logged in forza.")
        ErrorLogger.run(traceback.format_exc())


@forza.command()
async def time(ctx):
    time = ForzaSeason.time()
    await ctx.reply(f"Next seasons start in {time}.", mention_author=False)


@bot.command()
@commands.is_owner()
async def backup(ctx):
    ResponseBackup.run()
    with open(f"{here}\\bruhbot\\data.json", "r+") as f:
        data = json.load(f)
        now = date.today()
        data["lastbackup"] = now.strftime("%Y-%m-%d")
        f.seek(0)
        json.dump(data, f, indent=4)
    await ctx.reply("Response list saved to backup.", mention_author=False)


@bot.group(invoke_without_command=True, ignore_extra=False)
async def logs(ctx):
    if ctx.invoked_subcommand is None:

        class clearView(discord.ui.View):
            async def on_timeout(self) -> None:
                await self.msg.edit(view=None)
                self.stop()

            @discord.ui.button(style=discord.ButtonStyle.secondary, label="Clear Logs")
            async def buttonClear(self, interaction: discord.Interaction, button: discord.ui.Button):
                await interaction.response.defer()
                if interaction.user.id == 108105758578577408:
                    self.buttonClear.disabled = True
                    await self.msg.edit(view=self)
                    await clear(ctx)
                    self.stop()
                else:
                    await interaction.followup.send("You dare try to hide your crimes?", ephemeral=True)

        last = ErrorLogger.last()
        if last == "No logs found.":
            await ctx.reply(last, mention_author=False)
            return
        if len(last["error"]) >= 2000:
            ab = map(str.encode, last["error"])
            content = b"".join(ab)
            view = clearView(timeout=10)
            msg = await ctx.send(file=discord.File(BytesIO(content), "traceback.py"), view=view)
            view.msg = msg
            return
        else:
            view = clearView(timeout=10)
            msg = await ctx.send(f"{last['log']}, {last['time']}\n```py\n{last['error']}```", view=view)
            view.msg = msg


@logs.error
async def logs_error(ctx, error):
    if isinstance(error, commands.errors.TooManyArguments):
        await ctx.reply("Invalid Subcommand")
    else:
        await ctx.reply("Error logged in logs. Uh oh.")
        ErrorLogger.run(traceback.format_exc())


@logs.command()
@commands.is_owner()
async def clear(ctx):
    ErrorLogger.clear()
    await ctx.send("Error logs cleared.")


@clear.error
async def clear_error(ctx, error):
    if isinstance(error, commands.errors.NotOwner):
        await ctx.send("You dare try to hide your crimes?")
    else:
        await ctx.send("Error logged in logs clear.")
        ErrorLogger.run(traceback.format_exc())


@bot.command()
@commands.is_owner()
async def shutdown(ctx):
    await ctx.message.add_reaction("👋🏼")
    await bot.close()


bot.run(token)
