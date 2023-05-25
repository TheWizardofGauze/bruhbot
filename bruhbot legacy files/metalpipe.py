@bot.command()
async def metalpipe(ctx):
    if ctx.author.voice is None:
        await ctx.send('You must be in a voice channel to use this command')
        return
    
    channel = ctx.author.voice.channel
    vc = await channel.connect()
    vc.play(discord.FFmpegPCMAudio(executable=r".\bruhbot\ffmpeg\ffmpeg.exe", source=r".\bruhbot\jixaw metal sound.mp3"))
    while vc.is_playing():
        await asyncio.sleep(1)
    await vc.disconnect()
