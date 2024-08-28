import discord
from discord.ext import commands, tasks
from lib.sql import Guild

from repository.config import CONFIG
from repository.icons import Icons
from main import logger
import view.embeds as embeds

class Time(commands.Cog):

    def __init__(self, bot: discord.AutoShardedBot):
        print('Status ready')
        self.bot = bot
        self.change_status.start()

    @tasks.loop(minutes=5)
    async def change_status(self):
        bot = self.bot
        Guild.set_guilds(bot.guilds)
        count = Guild.get_count()
        await bot.change_presence(activity=discord.Game(name=f"厳選 Impactをプレイ中 / {count}サーバーで稼働中(累計) / Ver{CONFIG.version}",))

    @change_status.before_loop
    async def before(self):
        print("waiting")
        await self.bot.wait_until_ready()


def setup(bot: discord.AutoShardedBot):
    bot.add_cog(Time(bot))
