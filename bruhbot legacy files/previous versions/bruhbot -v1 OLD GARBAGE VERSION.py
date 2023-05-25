import discord, random
from discord.ext import commands
import time
client = discord.Client()

#trigger_words = ['nword', 'n-word', 'n word']
footer = 'Type $help <command> for more info on a command. You can also type $help <category> for more info on a category.'

async def send_dm(user: discord.User, content):
    channel = await user.create_dm()
    await channel.send(embed = content)

@client.event
async def on_ready():
    print('Connected')

@client.event
async def on_message(message):
    if not message.guild is None:
        name = message.guild.me.display_name.replace(" ", "").lower()
    elif message.guild is None:
        name = client.user.display_name.replace(" ", "").lower()
    channel = message.channel
    avatar = client.user.avatar_url
    content = message.content.lower()
    nospace = message.content.replace(" ", "").lower()
    replace = message.content.replace
    startswith = message.content.startswith
    
    if message.author == client.user:
        return
    
    if name in nospace or client.user in message.mentions:
        responses = []
        with open('responses.txt', 'r') as f:
            for line in f:
                current = line[:-1]
                responses.append(current)
        response = random.choice(responses)
        await channel.send(response)
        print (message.content)
        print (response)

    if startswith('$addr '):
        pre = replace('$addr ', '')
        with open('responses.txt', 'r') as f:
            file = f.readlines()
            for line in file:
                if pre.lower() == line.lower().strip('\n'):
                    await channel.send('Error: Response already exists')
                    return
        f = open('responses.txt', 'a')
        f.write(pre +'\n')
        
        f.close()
        await channel.send(':ok_hand:')
    elif startswith('$addr') or startswith('$help addr'):
        msg = discord.Embed(title='', description='`Syntax: $addr <word/phrase>`', color = 0xe74c3c)
        msg.set_author(name='N Word Help Menu', icon_url=avatar)
        msg.add_field(name='Add responses', value='Adds a new response to the list')
        msg.set_footer(text=footer)
        await channel.send(embed = msg)

    if startswith('$delr '):
        pre = replace('$delr ', '')
        with open('responses.txt', 'r') as f:
            file = f.readlines()
            found = False
            for line in file:
                if pre.lower() == line.lower().strip('\n'):
                    found = True
            if not found:
                await channel.send('Error: Response not found')
                return
        with open('responses.txt', 'w') as f:
            for line in file:
                if line.strip('\n').lower() != pre.lower():
                    f.write(line)
        await channel.send(':ok_hand:')
    elif startswith('$delr') or startswith('$help delr'):
        msg = discord.Embed(title='', description='`Syntax: $delr <word/phrase>`', color = 0xe74c3c)
        msg.set_author(name='N Word Help Menu', icon_url=avatar)
        msg.add_field(name='Delete responses', value='Deletes a response from the list.\nUse `$rlist` to check the list of responses')
        msg.set_footer(text=footer)
        await channel.send(embed = msg)

    if content == '$rlist':
        responses = []
        with open('responses.txt', 'r') as file:
            for line in file:
                current = line[:-1]
                responses.append(current)
        await channel.send(responses)
    elif content == '$help rlist':
        msg = discord.Embed(title='', description='`Syntax: $rlist`', color = 0xe74c3c)
        msg.set_author(name='N Word Help Menu', icon_url=avatar)
        msg.add_field(name='Show response list', value='Displays the list of possible responses')
        msg.set_footer(text=footer)
        await channel.send(embed = msg)

    if content == '$help':
            if message.guild == None:
                print('DM!')
                time.sleep(3)
            else:
                print('Server!')
                time.sleep(10)
                
            msg = discord.Embed(title='*Red V3*', description='*Additional Commands*', color = 0xe74c3c)
            msg.set_author(name='N Word Help Menu', icon_url=avatar)
            msg.add_field(name='__**Response**__', value=('**addr** Add a new response to the list \n'+
                                                                '**delr** Remove a response from the list \n'+
                                                                '**rlist** View the list of current responses'),inline=False)
            msg.set_footer(text=footer)
            user = message.author
            await send_dm(user, msg)
        
    if startswith('$shutdown') and message.author.id == 108105758578577408:
        await message.add_reaction('👋🏼')
        exit()


client.run('NjA4OTQ2OTU4Mjg3MTEwMTY0.XmWsNQ.IW8_1YO37SlpjbQvvS5kkJXxYC4')
