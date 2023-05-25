import asyncio
from concurrent.futures.thread import ThreadPoolExecutor
from redbot.core import commands
from datetime import date
from dateutil.relativedelta import relativedelta
from discord.ext import tasks
import json
import re
from threading import Thread
import wptools

class CI(Exception):
        pass

class OPBR(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.file = r"C:\Users\Ian\Desktop\Folders\Redbot\bruhbot\cogs\opbr\OPBR.json"
        with open(self.file) as f:
            data = json.load(f)
            names = []
            for name in data['names']:
                if data[name]['dead'] == 0:
                    names.append(name)
            self.names = names
            self.executor = ThreadPoolExecutor(max_workers=1)

    @commands.command(name='update')
    async def update(self, ctx):
        loop = asyncio.get_event_loop()
        while True:
            await loop.run_in_executor(self.executor, self._update)
   
    async def _update(self, ctx):
        await ctx.send('Updating battle royale list. This may take a few minutes.')
        today = date.today()
        ci = CI()

        for name in self.names:
            try:
                with open(self.file, 'r+') as f:
                    data = json.load(f)
                    
                    page = wptools.page(name, silent=True).get_parse()
                    info = page.data['infobox']
                    
                    for i, j in info.items():
                        if i == 'birth_date':
                            birth_date = re.sub('[^0-9|]', '', j)
                            birth_date = list(filter(None, birth_date.split('|')))
                            birth_date = date(year=int(birth_date[0]), month=int(birth_date[1]), day=int(birth_date[2]))
                            break
                    
                    for i, j in info.items():
                        if i == 'death_date':
                            death_date = re.sub('[^0-9|]', '', j)
                            death_date = list(filter(None, death_date.split('|')))
                            death_date = date(year=int(death_date[0]), month=int(death_date[1]), day=int(death_date[2]))

                            age = relativedelta(death_date, birth_date).years

                            await ctx.send(f'{name} has died at age {age} years old')
                            data[name]['age'] = age
                            data[name]['dead'] = 1
                            f.seek(0)
                            json.dump(data, f, indent=4)
                            f.truncate()

                            raise ci

                    age = relativedelta(today, birth_date).years

                    if not int(data[name]['age']) == age:
                        await ctx.send(f'{name} is now {age} years old')
                        data[name]['age'] = age
                        f.seek(0)
                        json.dump(data, f, indent=4)
                        f.truncate()
            except CI:
                continue
        await ctx.send('Finished updating.')