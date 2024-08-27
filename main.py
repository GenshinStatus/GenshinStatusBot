from repository.config import CONFIG
import discord
from discord.ext import commands
import os
import lib.sql as sql
import asyncio
import yaml_trans
import logging

# set logging
logger = logging.getLogger(__name__)
if CONFIG.debug:
    level = logging.DEBUG
else:
    level = logging.INFO
logging.basicConfig(
    level=level,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    datefmt="[%X]"
)

# set bot setting
intents = discord.Intents.default()
intents.guilds = True
bot = commands.AutoShardedBot(intents=intents)
TOKEN = os.getenv(f"TOKEN")

path = "./cogs"

@bot.event
async def on_application_command_error(ctx: discord.ApplicationContext, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.respond(error)
    elif isinstance(error, commands.MissingPermissions):
        await ctx.respond(content="BOT管理者限定コマンドです", ephemeral=True)
    else:
        raise error

@bot.event
async def on_guild_join(guild: discord.Guild):
    logger.info(f"新規導入サーバー: {guild.name}")
    sql.Ephemeral.init_ephemeral(guild.id)

@bot.event
async def on_ready():
    logger.info(f"{bot.user} On ready")
    yaml_trans.init(bot.user.id)
    await guildsCount()

async def sendChannel(id) -> discord.PartialMessageable:
    channel: discord.PartialMessageable = bot.get_partial_messageable(id)
    return channel

async def guildsCount():
    sql.Guild.set_guilds(bot.guilds)
    await asyncio.sleep(10)  # 複数のBOTを同時に再起動するときにちょっとあけとく
    count = sql.Guild.get_count()
    await bot.change_presence(activity=discord.Game(name=f"厳選 Impactをプレイ中 / {count}サーバーで稼働中(累計) / Ver{CONFIG.version}",))

async def reload_cogs():
    for cog in CONFIG.cogs_list:
        bot.reload_extension(f'cogs.{cog}')

for cog in CONFIG.cogs_list:
    bot.load_extension(f'cogs.{cog}', store=False)

bot.run(TOKEN)
