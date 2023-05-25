import asyncio
from datetime import date
from dateutil.relativedelta import relativedelta
import discord
from discord.ext import commands
import json
import os
import random
import re
import ResponseBackup

bot = commands.Bot('$')
bot.remove_command('help')
with open("data.json") as data:
    token = json.load(data)['token']

async def check_age():
    while True:
        def plural(num):
            if num == 1:
                return 0
            else:
                return 1
        now = date.today()
        bday = date(2020, 3, 8)
        rdelta = relativedelta(now, bday)
        year = ['year', 'years']
        if rdelta.months == 0 and rdelta.days == 0:
            await bot.change_presence(activity=discord.Game(name=f"god for {rdelta.years} {year[plural(rdelta.years)]}"))
        else:
            await bot.change_presence(status=discord.Status.online)
        await asyncio.sleep(3600)

async def send_dm(user: discord.User, content):
    dm = await user.create_dm()
    await dm.send(embed = content)

async def get_color(ctx):
    if ctx.guild:
        color = ctx.guild.get_member(bot.user.id).top_role.color
        return color
    else:
        color = 0xe74c3c
        return color

async def embed(ctx, name, description, content, color):
    embed = discord.Embed(title='*Bruhbot*', description=description, color=color)
    embed.set_author(name=f'{ctx.me.display_name} Help Menu', icon_url=bot.user.avatar_url)
    embed.add_field(name=name, value=content, inline=False)
    embed.set_footer(text='Type $help <command> for more info on a command. You can also type $help <category> for more info on a category.')
    return embed

async def send_image(ctx, response):
    try:
        os.chdir(".\\images")
        image = response.replace(' - image','')
        await ctx.channel.send(file=discord.File(image))
        os.chdir("..")
    except Exception as e:
        await ctx.channel.send(f'{e}.  I\'m telling <@108105758578577408>')
        os.chdir("..")
        return

@bot.event
async def on_ready():
    servers = list(bot.guilds)
    print(f'{bot.user.name}(ID:{bot.user.id}) connected to {str(len(servers))} servers')
    await check_age()

@bot.event
async def on_message(msg):
    ctx = await bot.get_context(msg)

    if ctx.author.bot:
        return

    nospace = re.sub('[^a-zA-Z0-9]', '', msg.content).lower()
    name = re.sub('[^a-zA-Z0-9]', '', ctx.me.display_name).lower()

    if name in nospace or bot.user in msg.mentions:
        responses = []
        os.chdir(os.path.dirname(__file__))
        with open('responses.txt', 'r') as f:
            for line in f:
                current = line[:-1]
                responses.append(current)
        response = random.choice(responses)
        if response.endswith('- image'):
            await send_image(ctx, response)
            return
            
        await ctx.send(response)
        return
    
    if '69' in nospace:
        await ctx.send('nice')
        return
        
    await bot.process_commands(msg)

@bot.command()
async def addr(ctx, *arg):
    if ctx.message.attachments:
        pic_ext = ['.jpg', '.png', '.jpeg', '.gif']
        for attachment in ctx.message.attachments:
            if any(attachment.filename.lower().endswith(ext) for ext in pic_ext):
                ext = '.'+attachment.filename.split('.',1)[1]
                os.chdir(os.path.dirname(__file__))
                with open('responses.txt', 'r') as f:
                    if arg:
                        pre = ''.join(arg[:])+ext
                    else:
                        pre = attachment.filename
                    file = f.readlines()
                    for line in file:
                        if pre.lower() == line.lower().replace(' - image\n',''):
                            await ctx.send('Error: Response already exists')
                            return
                os.chdir(".\\images")
                await attachment.save(pre)
            else:
                await ctx.send('Error: Invalid file type')
                return 
        os.chdir("..")
        with open('responses.txt', 'a') as f:
            f.write(f'{pre} - image\n')# type: ignore
        await ctx.send(':ok_hand:')
        await ctx.send('Image was added')
        return

    if not arg:
        helpName = 'Add responses'
        helpDes = '`Syntax: $addr <word/phrase>`'
        helpCont = 'Adds a new response to the list'
        helpColor = await get_color(ctx)
        msg = await embed(ctx, helpName, helpDes, helpCont, helpColor)
        await ctx.send(embed = msg)
        return
    
    os.chdir(os.path.dirname(__file__))
    with open('responses.txt', 'r') as f:
        pre=" ".join(arg[:])    
        file = f.readlines()
        for line in file:
            if pre.lower() == line.lower().strip('\n'):
                await ctx.send('Error: Response already exists')
                return
            
    with open('responses.txt', 'a') as f:
        f.write(pre+'\n')
    await ctx.send(':ok_hand:')
    await ctx.send(f"**\'{pre}\'** was added")

@bot.command()
async def delr(ctx):
    if not ctx.guild:
        await ctx.send('This command cannot be run from a DM')
        return
    start = 0
    end = 5
    pages = 0
    curPage = 1
    responses = []
    numbered = []
    color = await get_color(ctx)
    os.chdir(os.path.dirname(__file__))
    with open('responses.txt', 'r') as f:
        file = f.readlines()
        for line in file:
            current = line[:-1]
            responses.append(current)
            
    while pages < len(responses) / 5:
        pages += 1
        
    for i, j in enumerate(responses[start:end],1):
        j = str(i)+': '+j
        numbered.append(j)
        
    content = '\n'.join(numbered)
    msg = discord.Embed(title='Delete response', description=f"**Page {curPage}/{pages}:**\n{content}", color = color)
    message = await ctx.send(embed = msg)
    await message.add_reaction('1\u20e3')
    await message.add_reaction('2\u20e3')
    await message.add_reaction('3\u20e3')
    await message.add_reaction('4\u20e3')
    await message.add_reaction('5\u20e3')
    await message.add_reaction('⏮️')
    await message.add_reaction('◀️')
    await message.add_reaction('▶️')
    await message.add_reaction('⏭️')
    await message.add_reaction('❌')
    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in ['⏮️', '◀️', '▶️', '⏭️', '1\u20e3', '2\u20e3', '3\u20e3', '4\u20e3', '5\u20e3', '✅', '❌']
    
    while True:
        try:
            reaction, user = await bot.wait_for("reaction_add", timeout = 30, check = check)
            if str(reaction.emoji) == '1\u20e3':
                choice = 0
                await message.delete()
                break
            
            elif str(reaction.emoji) == '2\u20e3':
                choice = 1
                await message.delete()
                break
            
            elif str(reaction.emoji) == '3\u20e3':
                choice = 2
                await message.delete()
                break
            
            elif str(reaction.emoji) == '4\u20e3':
                choice = 3
                await message.delete()
                break
            
            elif str(reaction.emoji) == '5\u20e3':
                choice = 4
                await message.delete()
                break
            
            elif str(reaction.emoji) == '▶️' and curPage != pages:
                curPage += 1
                start += 5
                end += 5
                numbered = []
                for i, j in enumerate(responses[start:end],1):
                    j = str(i)+': '+j
                    numbered.append(j)
                content = '\n'.join(numbered)
                msg = discord.Embed(title='Delete response', description=f"**Page {curPage}/{pages}:**\n{content}", color = color)
                await message.edit(embed = msg)
                await message.remove_reaction(reaction, user)
                
            elif str(reaction.emoji) == '◀️' and curPage > 1:
                curPage -= 1
                start -= 5
                end -= 5
                numbered = []
                for i, j in enumerate(responses[start:end],1):
                    j = str(i)+': '+j
                    numbered.append(j)
                content = '\n'.join(numbered)
                msg = discord.Embed(title='Delete response', description=f"**Page {curPage}/{pages}:**\n{content}", color = color)
                await message.edit(embed = msg)
                await message.remove_reaction(reaction, user)
                
            elif str(reaction.emoji) == '⏭️' and curPage != pages:
                curPage = pages
                start = pages*5-5
                end = pages*5
                numbered = []
                for i, j in enumerate(responses[start:end],1):
                    j = str(i)+': '+j
                    numbered.append(j)
                content = '\n'.join(numbered)
                msg = discord.Embed(title='Delete response', description=f"**Page {curPage}/{pages}:**\n{content}", color = color)
                await message.edit(embed = msg)
                await message.remove_reaction(reaction, user)

            elif str(reaction.emoji) == '⏮️' and curPage > 1:
                curPage = 1
                start = 0
                end = 5
                numbered = []
                for i, j in enumerate(responses[start:end],1):
                    j = str(i)+': '+j
                    numbered.append(j)
                content = '\n'.join(numbered)
                msg = discord.Embed(title='Delete response', description=f"**Page {curPage}/{pages}:**\n{content}", color = color)
                await message.edit(embed = msg)
                await message.remove_reaction(reaction, user)
            
            elif str(reaction.emoji) == '❌':
                await message.delete()
                try:
                    await ctx.message.delete()
                except Exception:
                    pass
                return
                
            else:
                await message.remove_reaction(reaction, user)
                
        except asyncio.TimeoutError:
            await message.delete()
            try:
                await ctx.message.delete()
            except Exception:
                pass
            return

    if choice+1 > len(responses[start:end]):
        await ctx.send('Invalid selection.')
        return

    msg = discord.Embed(title='Delete response', description=f"Are you sure you want to delete this response?: \n**{responses[start:end][choice]}**", color = color)
    message = await ctx.send (embed = msg)
    await message.add_reaction('✅')
    await message.add_reaction('❌')
    while True:
        try:
            reaction, user = await bot.wait_for("reaction_add", timeout = 10, check = check)
            if str(reaction.emoji) == '✅':
                os.chdir(os.path.dirname(__file__))
                with open('responses.txt', 'w') as f:
                    for line in file:
                        if line.strip('\n').lower() != responses[start:end][choice].lower():
                            f.write(line)
                if ' - image' in responses[start:end][choice]:
                    try:
                        image = responses[start:end][choice].replace(' - image','')
                        os.chdir(".\\images")
                        os.remove(image)
                        os.chdir("..")
                    except Exception as e:
                        print(f'{e}.  Passing...')
                        os.chdir("..")
                        pass

                await message.delete()
                await ctx.send(':ok_hand:')
                await ctx.send(f"**\'{responses[start:end][choice]}\'** was deleted")
                break
                
            elif str(reaction.emoji) == '❌':
                await message.delete()
                try:
                    await ctx.message.delete()
                except Exception:
                    pass
                break
            
        except asyncio.TimeoutError:
            await message.delete()
            break

@bot.command()
async def rlist(ctx):
    start = 0
    end = 25
    pages = 0
    curPage = 1
    responses = []
    numbered = []
    color = await get_color(ctx)
    os.chdir(os.path.dirname(__file__))
    with open('responses.txt', 'r') as f:
        file = f.readlines()
        for line in file:
            current = line[:-1]
            responses.append(current)
            
    while pages < len(responses) / 25:
        pages += 1

    while not curPage > pages:
        numbered = []
        for i, j in enumerate(responses,1):
            j = str(i)+': '+j
            numbered.append(j)
        content = '\n'.join(numbered[start:end])
        msg = discord.Embed(title='Response list', description=f"**Page {curPage}/{pages}:**\n{content}", color = color)
        await ctx.send(embed = msg)
        start += 25
        end += 25
        curPage += 1

@bot.command()
async def help(ctx, *arg):
    pre=" ".join(arg[:]).lower()
        
    if pre == 'addr':
        helpName = 'Add responses'
        helpDes = '`Syntax: $addr <word/phrase>`'
        helpCont = 'Adds a new response to the list'
        helpColor = await get_color(ctx)
        msg = await embed(ctx, helpName, helpDes, helpCont, helpColor)
        await ctx.send(embed = msg)
        
    elif pre == 'delr':
        helpName = 'Delete responses'
        helpDes = '`Syntax: $delr`'
        helpCont = 'Displays a menu that allows a user to delete a specific response'
        helpColor = await get_color(ctx)
        msg = await embed(ctx, helpName, helpDes, helpCont, helpColor)
        await ctx.send(embed = msg)
        
    elif pre == 'rlist':
        helpName = 'Show response list'
        helpDes = '`Syntax: $rlist`'
        helpCont = 'Displays the list of possible responses'
        helpColor = await get_color(ctx)
        msg = await embed(ctx, helpName, helpDes, helpCont, helpColor)
        await ctx.send(embed = msg)
    
    elif pre == 'age':
        helpName = 'Check bot age'
        helpDes = '`Syntax: $age`'
        helpCont = 'Returns number of years/months/days since creation'
        helpColor = await get_color(ctx)
        msg = await embed(ctx, helpName, helpDes, helpCont, helpColor)
        await ctx.send(embed = msg)

    elif pre == 'response':
        helpName = '__**Response**__'
        helpDes = ''
        helpCont = ('**addr** Add a new response to the list \n'+
                    '**delr** Remove a response from the list \n'+
                    '**rlist** View the list of current responses')
        helpColor = await get_color(ctx)
        msg = await embed(ctx, helpName, helpDes, helpCont, helpColor)
        await ctx.send(embed = msg)
        
    elif not arg:
        helpName = '__**Response**__'
        helpDes = ''
        helpCont = ('**addr** Add a new response to the list \n'+
                    '**delr** Remove a response from the list \n'+
                    '**rlist** View the list of current responses')
        helpColor = await get_color(ctx)
        msg = await embed(ctx, helpName, helpDes, helpCont, helpColor)
        helpName2 = '__**Extra stuff**__'
        helpDes2 = ''
        helpCont2 = ('**age** Returns the current age of the bot')
        msg2 = await embed(ctx, helpName2, helpDes2, helpCont2, helpColor)
        user = ctx.author
        await send_dm(user, msg)
        await send_dm(user, msg2)
    else:
        return

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
    day = ['day', 'days']
    month = ['month', 'months']
    year = ['year', 'years']
    await ctx.send(f"I am {rdelta.years} {year[plural(rdelta.years)]}, {rdelta.months} {month[plural(rdelta.months)]}, {rdelta.days} {day[plural(rdelta.days)]} old")

@bot.command()
@commands.is_owner()
async def backup(ctx):
    ResponseBackup.run()
    await ctx.send('Response list saved to backup')

@bot.command()
@commands.is_owner()
async def shutdown(ctx):
    await ctx.message.add_reaction('👋🏼')
    await ctx.bot.logout()

bot.run(token)