import discord
from discord.ext import commands
from discord.commands import Option, SlashCommandGroup, OptionChoice
from model import notification
import lib.sql as sql

from repository.config import CONFIG
from repository.icons import Icons
from main import logger
import view.embeds as embeds

SELECT_EPHEMERAL = [
    OptionChoice(name='他人への表示をオンにする', value=0),
    OptionChoice(name='他人への表示をオフにする', value=1)
]

class SettingCog(commands.Cog):

    def __init__(self, bot):
        print('setting ready')
        self.bot = bot

    setting = SlashCommandGroup(
        name='setting',
        description='各種設定を行います。（サーバー管理者のみ）',
        default_member_permissions=discord.Permissions(
            administrator=True,
            moderate_members=True
        )
    )

    @setting.command(name='channel', description='通知を送るチャンネルを指定します')
    async def setting_channel(self, ctx: discord.ApplicationContext,
                  channel: Option(discord.TextChannel, required=True,description="通知を送るチャンネル")):

        embed = embeds.Embed(title="通知をこちらのチャンネルから送信します", description=f"サーバー名：{ctx.guild.name}\nチャンネル名：{channel.name}")
        messageble_channel = self.bot.get_partial_messageable(channel.id)
        try:
            await messageble_channel.send(embed=embed)
        except discord.errors.Forbidden:
            embed = embeds.ErrorEmbed(description=f"該当チャンネルではbotの権限が足りません。\nチャンネルの設定から、下記の画像のような項目で**botにメッセージを送信する権限が与えられているか**確認してください。")
            embed.add_field(name="必要な権限", value="チャンネルを見る、メッセージを送信")
            embed.add_field(name="権限不足のチャンネル", value=f"<#{channel.id}>")
            embed.set_image(
                url="https://genshin-cdn.cinnamon.works/notify/no_permission.jpg")
            await ctx.respond(embed=embed, ephemeral=sql.Ephemeral.is_ephemeral(ctx.guild_id))
            logger.info("/setting_channel - Fordidden_set")
            return
        notification.set_notification_channel(ctx.guild_id, channel.id)
        embed = embeds.Embed(title="設定しました。")
        await ctx.respond(embed=embed, ephemeral=sql.Ephemeral.is_ephemeral(ctx.guild_id))
        logger.info("/setting_channel - set")

    @setting.command(name='ephemeral', description='コマンドの使用が他人に表示するか設定できます。')
    async def setting_ephemeral(self, 
        ctx: discord.ApplicationContext,
        is_ephemeral_option: Option(int, name="コマンド履歴について", choices=SELECT_EPHEMERAL, required=True, description="ビルド画像など、自分が使ったコマンドの履歴を他人が見れるようにするか切り替えます。")):

        try:
            sql.Ephemeral.set_ephemeral(ctx.guild_id, is_ephemeral_option != 1)
        except discord.errors.Forbidden:
            embed = embeds.ErrorEmbed(description=f"何らかのエラーで失敗しました。")
            await ctx.respond(embed=embed, ephemeral=sql.Ephemeral.is_ephemeral(ctx.guild_id))
            return

        try:
            await ctx.respond(content="設定しました。", ephemeral=sql.Ephemeral.is_ephemeral(ctx.guild_id))
        except:
            sql.Ephemeral.init_ephemeral(ctx.guild_id)
            sql.Ephemeral.set_ephemeral(ctx.guild_id, False)
            await ctx.respond(content="設定しました。", ephemeral=sql.Ephemeral.is_ephemeral(ctx.guild_id))
        logger.info("/setting_ephemeral - set")

def setup(bot):
    bot.add_cog(SettingCog(bot))
