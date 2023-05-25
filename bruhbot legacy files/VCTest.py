import discord
from discord.ext import commands
import asyncio

bot = commands.Bot('#')

@bot.event
async def on_ready():
    print('ready')

### PLAY SOUND ON CHANNEL JOIN TEST ###
@bot.event
async def on_voice_state_update(member, before, after):
    try:
        if after.channel is not None:
            if after.channel.id == 384783523158032385 and not member == bot.user:#172571071059329026
                channel = bot.get_channel(384783523158032385)
                vc = member.voice.channel
                voice = discord.utils.get(bot.voice_clients, guild=384782692480188426)
                if voice == None:
                    vc = await vc.connect()
                async def check():
                    count = len(channel.members)
                    if count == 1:
                        await vc.disconnect()
                vc.play(discord.FFmpegPCMAudio(executable=r"C:\Users\Ian\Desktop\Folders\ffmpeg\ffmpeg.exe", source=r"C:\Users\Ian\Desktop\other\jixaw metal sound.mp3"))
                print(f"{member.display_name} joined the channel")
                while vc.is_playing():
                    await check()
                    await asyncio.sleep(.1)
                await vc.disconnect()
    except:
        pass

bot.run('NjA4OTQ2OTU4Mjg3MTEwMTY0.XmWsNQ.IW8_1YO37SlpjbQvvS5kkJXxYC4')
#ODI2OTY4MTU5MzczMjMwMTUw.YGUMHQ.2hHMdufy79MmYVwcUqqLg0TNV9M
