import discord, random
from discord.ext import commands
import asyncio
bot = commands.Bot('$')
bot.remove_command('help')

footer = 'Type $help <command> for more info on a command. You can also type $help <category> for more info on a category.'

async def send_dm(user: discord.User, content):
    channel = await user.create_dm()
    await channel.send(embed = content)

async def embed(name, description, content):
    embed = discord.Embed(title='*Red V3*', description=description, color = 0xe74c3c)
    embed.set_author(name='N Word Help Menu', icon_url=bot.user.avatar_url)
    embed.add_field(name=name, value=content, inline = False)
    embed.set_footer(text=footer)
    return embed

@bot.event
async def on_ready():
    print(bot.user.name+' connected')

@bot.event
async def on_message(message):
    if not message.guild is None:
        name = message.guild.me.display_name.lower().replace("bot", "").replace(" ", "")
        
    elif message.guild is None:
        name = bot.user.display_name.replace(" ", "").lower()
        
    channel = message.channel
    nospace = message.content.replace(" ", "").lower()

    if message.author == bot.user:
        return

    if name in nospace or bot.user in message.mentions:
        responses = []
        with open('responses.txt', 'r') as f:
            for line in f:
                current = line[:-1]
                responses.append(current)
        response = random.choice(responses)
        await channel.send(response)
        return
    
    if '69' in nospace:
        await channel.send('nice')
        return
        
    await bot.process_commands(message)

@bot.command()
async def addr(ctx, *arg):
    if ctx.message.attachments:
        await ctx.send('Error: Please only enter text. \nIf the reaction you are trying to add is an image please use the URL.')
        return
    if not arg:
        helpName = 'Add responses'
        helpDes = '`Syntax: $addr <word/phrase>`'
        helpMenu = 'Adds a new response to the list'
        msg = await embed(helpName, helpDes, helpMenu)
        await ctx.send(embed = msg)
        return
    
    with open('responses.txt', 'r') as f:
        pre=" ".join(arg[:])    
        file = f.readlines()
        for line in file:
            if pre.lower() == line.lower().strip('\n'):
                await ctx.send('Error: Response already exists')
                return
            
    f = open('responses.txt', 'a')
    f.write(pre+'\n')
    f.close()
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
    msg = discord.Embed(title='Delete response', description=f"**Page {curPage}/{pages}:**\n{content}", color = 0xe74c3c)
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
                msg = discord.Embed(title='Delete response', description=f"**Page {curPage}/{pages}:**\n{content}", color = 0xe74c3c)
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
                msg = discord.Embed(title='Delete response', description=f"**Page {curPage}/{pages}:**\n{content}", color = 0xe74c3c)
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
                msg = discord.Embed(title='Delete response', description=f"**Page {curPage}/{pages}:**\n{content}", color = 0xe74c3c)
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
                msg = discord.Embed(title='Delete response', description=f"**Page {curPage}/{pages}:**\n{content}", color = 0xe74c3c)
                await message.edit(embed = msg)
                await message.remove_reaction(reaction, user)
                
            else:
                await message.remove_reaction(reaction, user)
                
        except asyncio.TimeoutError:
            await message.delete()
            return

    if not len(responses[start:end]) == choice+1:
        await ctx.send('Invalid selection.')
        return
    msg = discord.Embed(title='Delete response', description=f"Are you sure you want to delete this response?: \n**{responses[start:end][choice]}**", color = 0xe74c3c)
    message = await ctx.send (embed = msg)
    await message.add_reaction('✅')
    await message.add_reaction('❌')
    while True:
        try:
            reaction, user = await bot.wait_for("reaction_add", timeout = 10, check = check)
            if str(reaction.emoji) == '✅':
                with open('responses.txt', 'w') as f:
                    for line in file:
                        if line.strip('\n').lower() != responses[start:end][choice].lower():
                            f.write(line)
                            
                await message.delete()
                await ctx.send(':ok_hand:')
                await ctx.send(f"**\'{responses[start:end][choice]}\'** was deleted")
                break
                
            elif str(reaction.emoji) == '❌':
                await message.delete()
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
        msg = discord.Embed(title='Response list', description=f"**Page {curPage}/{pages}:**\n{content}", color = 0xe74c3c)
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
        helpMenu = 'Adds a new response to the list'
        msg = await embed(helpName, helpDes, helpMenu)
        await ctx.send(embed = msg)
        
    elif pre == 'delr':
        helpName = 'Delete responses'
        helpDes = '`Syntax: $delr`'
        helpMenu = 'Displays a menu that allows a user to delete a specific response'
        msg = await embed(helpName, helpDes, helpMenu)
        await ctx.send(embed = msg)
        
    elif pre == 'rlist':
        helpName = 'Show response list'
        helpDes = '`Syntax: $rlist`'
        helpMenu = 'Displays the list of possible responses'
        msg = await embed(helpName, helpDes, helpMenu)
        await ctx.send(embed = msg)

    elif pre == 'response':
        helpName = '__**Response**__'
        helpDes = ''
        helpMenu = ('**addr** Add a new response to the list \n'+
                    '**delr** Remove a response from the list \n'+
                    '**rlist** View the list of current responses')
        msg = await embed(helpName, helpDes, helpMenu)
        await ctx.send(embed = msg)
        
    elif not arg:
        if ctx.guild is None:
            await asyncio.sleep(3)
        else:
            await asyncio.sleep(10)
        helpName = '__**Response**__'
        helpDes = ''
        helpMenu = ('**addr** Add a new response to the list \n'+
                    '**delr** Remove a response from the list \n'+
                    '**rlist** View the list of current responses')
        msg = await embed(helpName, helpDes, helpMenu)
        user = ctx.author
        await send_dm(user, msg)
    else:
        return

@bot.command()
async def shutdown(ctx):
    if await bot.is_owner(ctx.author):
        await ctx.message.add_reaction('👋🏼')
        exit()
    
bot.run('NjA4OTQ2OTU4Mjg3MTEwMTY0.XmWsNQ.IW8_1YO37SlpjbQvvS5kkJXxYC4')
