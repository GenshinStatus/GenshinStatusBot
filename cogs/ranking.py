from lib.yamlutil import yaml
import lib.sql as sql
import discord
from discord.ext import commands
from discord import Option, OptionChoice, SlashCommandGroup, option
import lib.ranking


class RankingCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    command_group = SlashCommandGroup('ranking', '原神ランキング')

    @command_group.command(name="set", description="ランキングに登録します。")
    async def set(
            self,
            ctx: discord.ApplicationContext):
        """ランキングに登録します。

        Args:
            ctx (discord.ApplicationContext): コンテキスト

        Returns:
            None: None    
        """
        # TODO: UserのUIDが登録されているか確認する

        # TODO: Viewでキャラクターの選択肢を提示する
        await ctx.send("ランキングに登録しました。")

    @command_group.command(name="me", description="自分のランキングを表示します。")
    async def me(
            self,
            ctx: discord.ApplicationContext):
        """ランキングを表示します。

        Args:
            ctx (discord.ApplicationContext): コンテキスト

        Returns:
            None: None    
        """
        # TODO: ランキングの画像を取得して表示する
        pass

    @command_group.command(name="remove", description="ランキングから自分のデータを削除します。")
    async def remove_all(
            self,
            ctx: discord.ApplicationContext):
        """ランキングから自分のデータを削除します。

        Args:
            ctx (discord.ApplicationContext): コンテキスト

        Returns:
            None: None    
        """
        # TODO: 確認用のButtonを表示して、削除するか確認する
        pass

    @command_group.command(name="show", description="ランキングを表示します。")
    async def show_list(
            self,
            ctx: discord.ApplicationContext):
        """ランキングを表示します。

        Args:
            ctx (discord.ApplicationContext): コンテキスト

        Returns:
            None: None    
        """
        # TODO: なんか良い感じにランキングを表示する。
        pass


def setup(bot):
    bot.add_cog(RankingCog(bot))
