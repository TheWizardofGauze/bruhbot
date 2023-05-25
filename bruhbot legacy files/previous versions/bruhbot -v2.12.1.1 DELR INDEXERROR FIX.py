import asyncio
from datetime import date
import json
import os
import random
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
here = os.path.dirname(__file__)


async def check_age():
    def plural(num):
        if num == 1:
            return 0
        else:
            return 1

    while True:
        now = date.today()
        bday = date(2020, 3, 8)
        rdelta = relativedelta(now, bday)
        year = ["year", "years"]
        if rdelta.months == 0 and rdelta.days == 0:
            await bot.change_presence(
                activity=discord.Game(
                    name=f"god for {rdelta.years} {year[plural(rdelta.years)]}"
                )
            )
        else:
            await bot.change_presence(status=discord.Status.online)
        await asyncio.sleep(3600)


async def send_dm(user: discord.User, content):
    dm = await user.create_dm()
    await dm.send(embed=content)


async def get_color(ctx):
    if ctx.guild:
        color = ctx.guild.get_member(bot.user.id).top_role.color
        return color
    else:
        color = 0xE74C3C  # red
        return color


async def embed(ctx, name, description, color, pages):
    embed = discord.Embed(color=color)
    if pages > 1:
        embed.title = "*Bruhbot*"
        for page in range(pages):
            embed.add_field(name=name[page], value=description[page], inline=False)
    else:
        embed.description = description
    embed.set_author(
        name=f"{ctx.me.display_name} Help Menu", icon_url=bot.user.display_avatar
    )
    embed.set_footer(
        text="Type $help <command> for more info on a command. You can also type $help <category> for more info on a category."
    )
    return embed


async def send_image(ctx, response):
    try:
        os.chdir(f"{here}\\images")
        image = response.replace(" - image", "")
        await ctx.send(file=discord.File(image))
        os.chdir("..")
    except Exception:  # missing image
        await ctx.send("Error logged.")
        e = traceback.format_exc()
        ErrorLogger.run(e)
        os.chdir("..")
        return


@bot.event
async def on_ready():
    servers = list(bot.guilds)
    print(f"{bot.user.name}(ID:{bot.user.id}) connected to {str(len(servers))} servers")
    await check_age()


@bot.event
async def on_message(msg):
    await bot.process_commands(msg)
    ctx = await bot.get_context(msg)
    if ctx.author.bot or ctx.channel.id == 1040461583027011645:
        return
    nospace = re.sub("[^a-zA-Z0-9]", "", msg.content).lower()
    name = re.sub("[^a-zA-Z0-9]", "", ctx.me.display_name).lower()
    if (
        name in nospace
        or bot.user in msg.mentions
        or (msg.reference != None and msg.reference.resolved.author == bot.user)
    ):
        responses = []
        with open(f"{here}\\bruhbot\\responses.txt", "r", encoding="utf-8") as f:
            for line in f:
                current = line[:-1]
                responses.append(current)
        response = random.choice(responses).replace(r"\n", "\n")
        if response.endswith("- image"):
            await send_image(ctx, response)
            return
        await ctx.send(response)
        return
    if "69" in nospace:
        await ctx.send("nice")  # nice
        return


@bot.command()
async def addr(ctx, *, arg: str = None):
    try:
        if ctx.message.attachments:  # image support
            invalid_counter = 0
            dupe_counter = 0
            for attachment in ctx.message.attachments:
                dupe = False
                if "image" in attachment.content_type:
                    ext = os.path.splitext(attachment.filename)[-1]
                    with open(
                        f"{here}\\bruhbot\\responses.txt", "r", encoding="utf-8"
                    ) as f:
                        if arg and len(ctx.message.attachments) == 1:
                            pre = os.path.splitext("".join(arg[:]))[0] + ext
                        else:
                            if (
                                attachment.filename == f"image0{ext}"
                                or attachment.filename == f"unknown{ext}"
                                or attachment.filename == f"image{ext}"
                            ):
                                new = "".join(
                                    random.choice(string.ascii_letters + string.digits)
                                    for i in range(6)
                                )
                                while os.path.exists(f".\\images\\{new}"):
                                    new = new + "".join(random.choice(string.digits))
                                pre = new + ext
                            else:
                                pre = attachment.filename
                        file = f.readlines()
                        for line in file:
                            if pre.lower() == line.lower().replace(" - image\n", ""):
                                if len(ctx.message.attachments) == 1:
                                    await ctx.send(f"Error: **'{pre}'** already exists")
                                    return
                                else:
                                    dupe_counter += 1
                                    dupe = True
                                    break
                    if dupe == False:
                        os.chdir(f"{here}\\images")
                        await attachment.save(pre)
                        os.chdir("..")
                    else:
                        continue
                    with open(
                        f"{here}\\bruhbot\\responses.txt", "a", encoding="utf-8"
                    ) as f:
                        f.write(f"{pre} - image\n")
                else:
                    if len(ctx.message.attachments) == 1:
                        await ctx.send("Error: Invalid file type")
                        return
                    else:
                        invalid_counter += 1
            if (
                len(ctx.message.attachments) - invalid_counter == 1
                or len(ctx.message.attachments) - dupe_counter == 1
            ):
                added = "Image was added"
            elif (
                len(ctx.message.attachments) - invalid_counter == 0
                or len(ctx.message.attachments) - dupe_counter == 0
            ):
                added = "No images were added"
            else:
                added = "Images were added"
            if not invalid_counter == len(ctx.message.attachments):
                await ctx.send(":ok_hand:")
                await ctx.send(added)
            if dupe_counter > 0:
                await ctx.send(f"Blocked {str(dupe_counter)} duplicate files.")
            if invalid_counter > 0:
                await ctx.send(f"Blocked {str(invalid_counter)} invalid files.")
            return
        if not arg:
            await help(ctx, "addr")
            return
        with open(f"{here}\\bruhbot\\responses.txt", "r", encoding="utf-8") as f:
            pre1 = "".join(arg[:])
            pre = pre1.replace("\n", r"\n")
            file = f.readlines()
            for line in file:
                if pre.lower() == line.lower().strip("\n"):
                    await ctx.send("Error: Response already exists")
                    return
        with open(f"{here}\\bruhbot\\responses.txt", "a", encoding="utf-8") as f:
            f.write(pre + "\n")
        await ctx.send(":ok_hand:")
        await ctx.send(f"**'{pre1}'** was added")
    except Exception:
        await ctx.send("Error logged.")
        e = traceback.format_exc()
        ErrorLogger.run(e)


@bot.command()
async def delr(ctx, *arg):
    try:

        def get_list(responses, start, end, curPage):
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

        class menuView(discord.ui.View):
            async def on_timeout(self) -> None:
                emb = discord.Embed(title="Timeout", description="", color=color)
                # for item in self.children:
                #   item.disabled = True
                await self.msg.edit(embed=emb, view=None)
                self.timeout = True

            async def update(self):
                if self.curPage == 1:
                    self.buttonFirst.disabled = True
                    self.buttonBack.disabled = True
                else:
                    self.buttonFirst.disabled = False
                    self.buttonBack.disabled = False
                if self.curPage == self.pages:
                    self.buttonNext.disabled = True
                    self.buttonLast.disabled = True
                else:
                    self.buttonNext.disabled = False
                    self.buttonLast.disabled = False
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

            choice: bool = None
            cancel: bool = None
            first: bool = None
            back: bool = None
            next: bool = None
            last: bool = None

            @discord.ui.button(style=discord.ButtonStyle.danger, label="1")
            async def button1(
                self, interaction: discord.Interaction, button: discord.ui.Button
            ):
                self.choice = 0
                await self.msg.delete()
                self.stop()

            @discord.ui.button(style=discord.ButtonStyle.danger, label="2")
            async def button2(
                self, interaction: discord.Interaction, button: discord.ui.Button
            ):
                self.choice = 1
                await self.msg.delete()
                self.stop()

            @discord.ui.button(style=discord.ButtonStyle.danger, label="3")
            async def button3(
                self, interaction: discord.Interaction, button: discord.ui.Button
            ):
                self.choice = 2
                await self.msg.delete()
                self.stop()

            @discord.ui.button(style=discord.ButtonStyle.danger, label="4")
            async def button4(
                self, interaction: discord.Interaction, button: discord.ui.Button
            ):
                self.choice = 3
                await self.msg.delete()
                self.stop()

            @discord.ui.button(style=discord.ButtonStyle.danger, label="5")
            async def button5(
                self, interaction: discord.Interaction, button: discord.ui.Button
            ):
                self.choice = 4
                await self.msg.delete()
                self.stop()

            @discord.ui.button(
                style=discord.ButtonStyle.blurple,
                emoji=discord.PartialEmoji.from_str("⏮️"),
            )
            async def buttonFirst(
                self, interaction: discord.Interaction, button: discord.ui.Button
            ):
                await interaction.response.defer()
                self.curPage = 1
                self.start = 0
                self.end = 5
                emb = get_list(responses, self.start, self.end, self.curPage)
                await self.update()
                await self.msg.edit(embed=emb, view=self)

            @discord.ui.button(
                style=discord.ButtonStyle.blurple,
                emoji=discord.PartialEmoji.from_str("◀️"),
            )
            async def buttonBack(
                self, interaction: discord.Interaction, button: discord.ui.Button
            ):
                await interaction.response.defer()
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
            async def buttonNext(
                self, interaction: discord.Interaction, button: discord.ui.Button
            ):
                await interaction.response.defer()
                self.curPage += 1
                self.start += 5
                self.end += 5
                emb = get_list(responses, self.start, self.end, self.curPage)
                await self.update()
                await self.msg.edit(embed=emb, view=self)

            @discord.ui.button(
                style=discord.ButtonStyle.blurple,
                emoji=discord.PartialEmoji.from_str("⏭️"),
            )
            async def buttonLast(
                self, interaction: discord.Interaction, button: discord.ui.Button
            ):
                await interaction.response.defer()
                self.curPage = self.pages
                self.start = self.pages * 5 - 5
                self.end = self.pages * 5
                emb = get_list(responses, self.start, self.end, self.curPage)
                await self.update()
                await self.msg.edit(embed=emb, view=self)

            @discord.ui.button(
                style=discord.ButtonStyle.secondary,
                emoji=discord.PartialEmoji.from_str("❌"),
            )
            async def buttonCancel(
                self, interaction: discord.Interaction, button: discord.ui.Button
            ):
                self.cancel = True
                emb = discord.Embed(title="Canceled", description="", color=color)
                await self.msg.edit(embed=emb, view=None)
                self.stop()

        class confirmView(discord.ui.View):
            async def on_timeout(self) -> None:
                emb = discord.Embed(title="Timeout", description="", color=color)
                # for item in self.children:
                #    item.disabled = True
                await self.msg.edit(embed=emb, view=None)
                self.timeout = True

            confirm: bool = None
            cancel: bool = None

            @discord.ui.button(style=discord.ButtonStyle.success, label="Confirm")
            async def buttonConfirm(
                self, interaction: discord.Interaction, button: discord.ui.Button
            ):
                self.confirm = True
                await self.msg.delete()
                self.stop()

            @discord.ui.button(style=discord.ButtonStyle.danger, label="Cancel")
            async def buttonCancel(
                self, interaction: discord.Interaction, button: discord.ui.Button
            ):
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
                await ctx.send("Selection must be a number.")
                e = traceback.format_exc()
                ErrorLogger.run(e)
                return
            except IndexError:
                await ctx.send("Error: Selection out of range.")
                e = traceback.format_exc()
                ErrorLogger.run(e)
                return
            emb = discord.Embed(
                title="Delete response",
                description=f"Are you sure you want to delete this response?: \n**{responses[choice]}**",
                color=color,
            )
            cview = confirmView(timeout=10)
            msg = await ctx.send(embed=emb, view=cview)
            cview.msg = msg
            await cview.wait()
            if cview.confirm == True:
                with open(
                    f"{here}\\bruhbot\\responses.txt", "w", encoding="utf-8"
                ) as f:
                    for line in file:
                        if line.strip("\n").lower() != responses[choice].lower():
                            f.write(line)
                if " - image" in responses[choice]:
                    try:
                        image = responses[choice].replace(" - image", "")
                        os.remove(f"{here}\\images\\{image}")
                    except Exception as e:
                        print(f"{e}. Passing...")
                        ErrorLogger.run(e)
                        pass
                await ctx.send(":ok_hand:")
                await ctx.send(f"**'{responses[choice]}'** was deleted")
                return
            if cview.cancel == True or cview.timeout == True:
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
            if mview.cancel == True or mview.timeout == True:
                return
            if mview.choice is not None:
                if mview.choice + 1 > len(responses[mview.start : mview.end]):
                    await ctx.send("Invalid selection.")
                    return
                emb = discord.Embed(
                    title="Delete response",
                    description=f"Are you sure you want to delete this response?: \n**{responses[mview.start:mview.end][mview.choice]}**",
                    color=color,
                )
                cview = confirmView(timeout=10)
                msg = await ctx.send(embed=emb, view=cview)
                cview.msg = msg
                await cview.wait()
                if cview.confirm == True:
                    with open(
                        f"{here}\\bruhbot\\responses.txt", "w", encoding="utf-8"
                    ) as f:
                        for line in file:
                            if (
                                line.strip("\n").lower()
                                != responses[mview.start : mview.end][
                                    mview.choice
                                ].lower()
                            ):
                                f.write(line)
                    if " - image" in responses[mview.start : mview.end][mview.choice]:
                        try:
                            image = responses[mview.start : mview.end][
                                mview.choice
                            ].replace(" - image", "")
                            os.remove(f"{here}\\images\\{image}")
                        except Exception as e:
                            print(f"{e}. Passing...")
                            ErrorLogger.run(e)
                            pass
                    await ctx.send(":ok_hand:")
                    await ctx.send(
                        f"**'{responses[mview.start:mview.end][mview.choice]}'** was deleted"
                    )
                if cview.cancel == True or cview.timeout == True:
                    return

    except Exception:
        await ctx.send("Error logged.")
        e = traceback.format_exc()
        ErrorLogger.run(e)


@bot.command()
async def rlist(ctx):
    try:
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
        while not curPage > pages:
            content = "\n".join(numbered[start:end])
            msg = discord.Embed(
                title="Response list",
                description=f"**Page {curPage}/{pages}:**\n{content}",
                color=color,
            )
            await ctx.send(embed=msg)
            start += 25
            end += 25
            curPage += 1
            await asyncio.sleep(0.21)
    except Exception:
        await ctx.send("Error logged.")
        e = traceback.format_exc()
        ErrorLogger.run(e)


@bot.command()
@commands.is_owner()
async def rtest(ctx, arg):  # for testing responses
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
        await ctx.send("Error: Selection out of range")
        return
    response = responses[choice].replace(r"\n", "\n")
    if response.endswith("- image"):
        await send_image(ctx, response)
        return
    await ctx.send(response)


@bot.command()
async def help(ctx, *arg):
    try:
        pre = " ".join(arg[:]).lower()
        args = ["addr", "delr", "rlist", "age", "forza", "response", "extra"]
        if pre in args:
            with open(f"{here}\\bruhbot\\data.json") as f:
                data = json.load(f)
                helpDes = data[pre]["description"]
            helpColor = await get_color(ctx)
            msg = await embed(ctx, None, helpDes, helpColor, 1)
            await ctx.send(embed=msg)
        elif not arg:
            categories = ["response", "extra"]
            helpColor = await get_color(ctx)
            user = ctx.author
            helpName = []
            helpDes = []
            with open(f"{here}\\bruhbot\\data.json") as f:
                data = json.load(f)
                for cat in categories:
                    helpDes.append(data[cat]["description"])
                    helpName.append(data[cat]["name"])
                msg = await embed(
                    ctx,
                    helpName,
                    helpDes,
                    helpColor,
                    len(categories),
                )
                await send_dm(user, msg)
        else:
            return
    except Exception:
        await ctx.send("Error logged.")
        e = traceback.format_exc()
        ErrorLogger.run(e)


@bot.command()
async def age(ctx):
    def plural(num):
        if num == 1:
            return 0
        else:
            return 1

    now = date.today()
    bday = date(2020, 3, 8)
    rdelta = relativedelta(now, bday)
    plurals = [["year", "years"], ["month", "months"], ["day", "days"]]
    await ctx.send(
        f"I am {rdelta.years} {plurals[0][plural(rdelta.years)]}, {rdelta.months} {plurals[1][plural(rdelta.months)]}, {rdelta.days} {plurals[2][plural(rdelta.days)]} old"
    )


@bot.group(invoke_without_command=True, ignore_extra=False)
async def forza(ctx):
    if ctx.invoked_subcommand is None:
        season = ForzaSeason.season()
        await ctx.send(
            f"Horizon 4: {season[0].capitalize()}\nHorizon 5: {season[1].capitalize()}"
        )


@forza.error
async def forza_error(ctx, error):
    if isinstance(error, commands.errors.TooManyArguments):
        await help(ctx, "forza")


@forza.command()
async def time(ctx):
    time = ForzaSeason.time()
    await ctx.send(f"Next seasons start in {time}")


@bot.command()
@commands.is_owner()
async def backup(ctx):
    ResponseBackup.run()
    await ctx.send("Response list saved to backup")


@bot.group(invoke_without_command=True, ignore_extra=False)
async def logs(ctx):
    if ctx.invoked_subcommand is None:
        l = ErrorLogger.last()
        await ctx.send(l)


@logs.error
async def logs_error(ctx, error):
    if isinstance(error, commands.errors.TooManyArguments):
        await ctx.send("Invalid Subcommand")


@logs.command()
@commands.is_owner()
async def clear(ctx):
    ErrorLogger.clear()
    await ctx.send("Error logs cleared")


@clear.error
async def clear_error(ctx, error):
    if isinstance(error, commands.errors.NotOwner):
        await ctx.send("You dare try to hide your crimes?")


@bot.command()
@commands.is_owner()
async def shutdown(ctx):
    await ctx.message.add_reaction("👋🏼")
    await bot.close()


bot.run(token)
