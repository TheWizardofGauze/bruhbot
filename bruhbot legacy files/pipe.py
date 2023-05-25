import discord
from discord.ext import commands

bot = commands.Bot('$')

@bot.event
async def on_ready():
    print('ready')

@bot.command
async def pipe(ctx):
    vc = ctx.author.voice.channel
    voice = await vc.connect()
    
