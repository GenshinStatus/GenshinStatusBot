import discord
from discord.ext import commands, tasks
from discord.commands import Option, SlashCommandGroup
from datetime import datetime, timedelta
import time
from model import notification

from repository.config import CONFIG
from repository.icons import Icons
from main import logger
import view.embeds as embeds

def datetime_to_unixtime(dt: datetime) -> int:
    """datetime型からunix時間をintで返します。

    Args:
        dt (datetime): datetime型の時間

    Returns:
        int: unix時間
    """
    return round(int(time.mktime(dt.timetuple())), -1)


class NotificationCog(commands.Cog):

    def __init__(self, bot: discord.AutoShardedBot):
        print('Notification ready')
        self.bot = bot
        self.check_notification.start()

    notification = SlashCommandGroup('notification', 'test')

    @notification.command(name='resin', description='樹脂が200になる前に通知します')
    async def resin(self, 
                    ctx: discord.ApplicationContext,
                    resin: Option[int, required=True, description="現在の樹脂量", max_value=199, min_value=1],
                    times: Option[int, required=False, description="溢れる何分前に通知するか（未設定の場合は40分前）", max_value=120, min_value=1, default=40]):
        await ctx.response.defer(ephemeral=True)
        try:
            channel = notification.get_notification_channel(ctx.guild_id)
        except ValueError as e:
            await ctx.respond(content="通知チャンネルが設定されていません。サーバー管理者に連絡して設定してもらってください。```/setting channel```で設定できます。")
            logger.info(f"/notification - guild_id: {ctx.guild_id} -> チャンネル未登録")
            return

        plan_time = datetime.now() + timedelta(minutes=1600 - (resin*8))
        notification_time = (plan_time - timedelta(minutes=times))

        notification.add_notification(
            type_id=1,
            bot_id=ctx.bot.user.id,
            user_id=ctx.user.id,
            guild_id=ctx.guild_id,
            notification_time=notification_time,
            plan_time=plan_time,
        )

        embed = embeds.Embed(title=f"{notification_time.strftime('%Y/%m/%d %H:%M')}に通知を以下のチャンネルから送信します", description=f"チャンネル：<#{channel}>")
        await ctx.respond(content="設定しました。", embed=embed)
        logger.info(f"/notification_resin - set")

    @tasks.loop(seconds=10)
    async def check_notification(self):
        try:
            notification_times, notification_channel_dict = notification.executing_notifications_search(
                self.bot.user.id)
        except ValueError as e:
            return

        for notifi in notification_times:
            try:
                channel = self.bot.get_partial_messageable(
                    id=notification_channel_dict[notifi.guild_id])
                plan_time = datetime_to_unixtime(notifi.plan_time)
                embed = discord.Embed(title=f"{Icons.props.Resin} 樹脂通知", color=0x1e90ff,
                                      description=f"⚠あと約<t:{plan_time}:R>に樹脂が溢れます！")
                await channel.send(content=f"<@{notifi.user_id}>", embed=embed)
            except Exception as e:
                logger.error(e)
                pass
        notification.delete_notifications(
            notification_ids=tuple((
                v.notification_id for v in notification_times)),
        )
        logger.info("/notification_resin - 通知")

    @check_notification.before_loop
    async def before_check_notification(self):
        logger.debug('waiting...')
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(NotificationCog(bot))
