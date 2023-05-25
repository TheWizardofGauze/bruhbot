import discord, random
from discord.ext import commands
import asyncio
bot = commands.Bot('$')
bot.remove_command('help')

footer = 'Type $help <command> for more info on a command. You can also type $help <category> for more info on a category.'

async def send_dm(user: discord.User, content):
    channel = await user.create_dm()
    await channel.send(embed = content)

@bot.event
async def on_ready():
    print(bot.user.name+' connected')

@bot.event
async def on_message(message):
    if not message.guild is None:
        name = message.guild.me.display_name.replace(" ", "").lower()
        
    elif message.guild is None:
        name = bot.user.display_name.replace(" ", "").lower()
        
    channel = message.channel
    content = message.content.lower()
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
        
    await bot.process_commands(message)

@bot.command()
async def addr(ctx, *arg):
    if not arg:
        msg = discord.Embed(title='', description='`Syntax: $addr <word/phrase>`', color = 0xe74c3c)
        msg.set_author(name='N Word Help Menu', icon_url=bot.user.avatar_url)
        msg.add_field(name='Add responses', value='Adds a new response to the list')
        msg.set_footer(text=footer)
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

@bot.command()
async def delr(ctx, *arg):
    if not arg:
        msg = discord.Embed(title='', description='`Syntax: $delr <word/phrase>`', color = 0xe74c3c)
        msg.set_author(name='N Word Help Menu', icon_url=bot.user.avatar_url)
        msg.add_field(name='Delete responses', value='Deletes a response from the list.\nUse `$rlist` to check the list of responses')
        msg.set_footer(text=footer)
        await ctx.send(embed = msg)
        return
    
    with open('responses.txt', 'r') as f:
        pre=" ".join(arg[:])   
        file = f.readlines()
        found = False
        for line in file:
            if pre.lower() == line.lower().strip('\n'):
                found = True
        if not found:
            await ctx.send('Error: Response not found')
            return
        
    with open('responses.txt', 'w') as f:
        for line in file:
            if line.strip('\n').lower() != pre.lower():
                f.write(line)
                
    await ctx.send(':ok_hand:')

@bot.command()
async def rlist(ctx):
    responses = []
    with open('responses.txt', 'r') as f:
        for line in f:
            current = line[:-1]
            responses.append(current)
            
    await ctx.send(responses)

@bot.command()
async def help(ctx, *arg):
    pre=" ".join(arg[:])
        
    if pre == 'addr':
        helpName = 'Add responses'
        helpDes = '`Syntax: $addr <word/phrase>`'
        helpMenu = 'Adds a new response to the list'
        
    elif pre == 'delr':
        helpName = 'Delete responses'
        helpDes = '`Syntax: $delr <word/phrase>`'
        helpMenu = 'Deletes a response from the list.\nUse `$rlist` to check the list of responses'
        
    elif pre == 'rlist':
        helpName = 'Show response list'
        helpDes = '`Syntax: $rlist`'
        helpMenu = 'Displays the list of possible responses'
        
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
    else:
        return
        
    msg = discord.Embed(title='*Red V3*', description=helpDes, color = 0xe74c3c)
    msg.set_author(name='N Word Help Menu', icon_url=bot.user.avatar_url)
    msg.add_field(name=helpName, value=helpMenu, inline = False)
    msg.set_footer(text=footer)
    user = ctx.author
    
    await send_dm(user, msg)

@bot.command()
async def shutdown(ctx):
    if ctx.author.id == 108105758578577408:
        await ctx.message.add_reaction('👋🏼')
        exit()
    
bot.run('NjA4OTQ2OTU4Mjg3MTEwMTY0.XmWsNQ.IW8_1YO37SlpjbQvvS5kkJXxYC4')
