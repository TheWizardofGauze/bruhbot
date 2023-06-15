from redbot.core import commands
from discord.ext.commands import Bot
import discord
import lavalink


class Metalpipe(commands.Cog):
    bot = Bot("$", intents=discord.Intents.default())

    @bot.event
    async def on_ready(self, bot):
        await lavalink.initialize(
            bot, host="localhost", password="password", ws_port=2333
        )

    @commands.command(name="metalpipe")
    async def metalpipe(self, ctx):
        guild = ctx.guild.id
        vc = ctx.author.voice.channel
        if lavalink.get_player(guild) == None:
            player = await lavalink.connect(vc)
        else:
            player = lavalink.get_player(guild)
        lavalink.Node.connect(self)
        user = self.bot.get_user(ctx.author.id)
        track = await player.load_tracks("jixaw metal sound")
        player.add(user, track)
        await player.play()
