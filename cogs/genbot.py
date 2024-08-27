import discord
from discord.ui import Select, View
from discord.ext import commands, tasks
from discord.commands import Option, SlashCommandGroup
import datetime
from lib.yamlutil import yaml
import copy
import lib.now as getTime
import math
import google.calendar as calendar
import main
import time
import lib.sql as sql

from repository.config import CONFIG
from repository.icons import Icons
from main import logger
import view.embeds as embeds

l: list[discord.SelectOption] = []

class helpselectView(View):
    @discord.ui.select(
        placeholder="表示するヘルプコマンドを指定してください",
        options=[
            discord.SelectOption(
                    label=help.name,
                    emoji=help.emoji,
                    description=help.description,
            ) for help in CONFIG.help_list])
    
    async def select_callback(self, select: discord.ui.Select, interaction):
        help_commands = [
            {
                "name": help.name,
                "description": help.content,
                "value": help.value
            } for help in CONFIG.help_list
        ]

        embed = embeds.Embed(
            title=f"{select.values[0]}")
        
        for command in help_commands:
            if select.values[0] == command["name"]:
                logger.info(f"/help - {command['name']}")
                embed.add_field(
                    name=command["name"],
                    value=command["value"]
                )
                break
        
        await interaction.response.edit_message(content=None, embed=embed, view=self)


class TodayEmbed(embeds.Embed):
    def __init__(self, day_of_week: str, url: str):
        super().__init__(title=f"{day_of_week}の日替わり秘境はこちら")
        self.set_image(url=url)

    def get_embed(self):
        embed = copy.deepcopy(self)

        # 明日の5時
        daily = int(getTime.daily.timestamp() - time.time())
        result = f"約{daily//3600}時間{daily%3600//60}分"
        embed.add_field(inline=False, name=f"{Icons.props.Commission}  デイリー更新まで",
                        value=f"```ansi\n[33mあと{result}[0m```")
        # 明日の1時
        hoyo = int(getTime.hoyo.timestamp() - time.time())
        result = f"約{hoyo//3600}時間{hoyo%3600//60}分"
        embed.add_field(inline=False, name=f"{Icons.tools.HOYOLAB}  HoYoLabログインボーナス更新まで",
                        value=f"[ログインボーナスを受け取る](https://t.co/MnjUZfg7Dn)\n```ansi\n[33mあと{result}[0m```\n")
        # 曜日取得
        weekly = int(getTime.weekly.timestamp() - time.time())
        result = f"約{weekly//86400}日{weekly%86400//3600}時間{weekly%86400%3600//60}分"
        embed.add_field(inline=False, name=f"{Icons.props.WeekBoss}  週ボス等リセットまで",
                        value=f"```ansi\n[33mあと{result}[0m```")
        return embed


class DayOfWeekUnexploredRegion:
    def __init__(self, file_path: str):
        self.EMBEDS: dict[int, discord.Embed] = {}
        self.SELECT_OPTIONS: list[discord.SelectOption] = []
        data: dict = yaml(file_path).load_yaml()
        for k, v in data.items():
            self.__add_data(
                key=k, day_of_week=v["day_of_week"], url=v["url"])

    def __add_data(self, key, day_of_week, url):
        # embedの追加
        embed = TodayEmbed(day_of_week=day_of_week, url=url)
        self.EMBEDS[key] = embed
        # optionsの追加
        self.SELECT_OPTIONS.append(
            discord.SelectOption(label=day_of_week, value=str(key)))


DATA = DayOfWeekUnexploredRegion("weekday.yaml")


class weekselectView(View):
    def __init__(self):
        self.weekday = datetime.date.today().weekday()
        # タイムアウトを5分に設定してタイムアウトした時にすべてのボタンを無効にする
        super().__init__(timeout=300, disable_on_timeout=True)

    @discord.ui.button(label="今日の秘境に戻る")
    async def today(self, _: discord.ui.Button, interaction: discord.Interaction):
        self.weekday = datetime.date.today().weekday()
        await interaction.response.edit_message(embed=DATA.EMBEDS[self.weekday].get_embed(), view=self)
        logger.info(f"/genbot today - {self.weekday}")

    @discord.ui.button(label="次の日の秘境")
    async def nextday(self, _: discord.ui.Button, interaction: discord.Interaction):
        self.weekday = (self.weekday + 1) % 7
        await interaction.response.edit_message(embed=DATA.EMBEDS[self.weekday].get_embed(), view=self)
        logger.info(f"/genbot today - {self.weekday}")

    @discord.ui.select(
        placeholder="確認したい曜日を選択",
        options=DATA.SELECT_OPTIONS
    )
    async def select_callback(self, select: discord.ui.Select, interaction: discord.Interaction):
        self.weekday = int(select.values[0])
        view = self
        await interaction.response.edit_message(embed=DATA.EMBEDS[self.weekday].get_embed(), view=view)
        logger.info(f"/genbot today - {self.weekday}")

# バグ報告モーダル


class ReportModal(discord.ui.Modal):
    def __init__(self, select: str):
        super().__init__(title="レポート報告", timeout=300)
        self.select = select

        self.content = discord.ui.InputText(
            label="操作内容",
            style=discord.InputTextStyle.paragraph,
            placeholder="どのような操作で発生しましたか？",
            required=False,
        )
        self.add_item(self.content)
        self.result = discord.ui.InputText(
            label="バグによって生じたこと",
            style=discord.InputTextStyle.paragraph,
            placeholder="例：インタラクションに失敗した、メッセージが大量に表示された等",
            required=True,
        )
        self.add_item(self.result)

    async def callback(self, interaction: discord.Interaction) -> None:
        embed = embeds.LoadingEmbed()
        await interaction.response.edit_message(content=None, embed=embed)
        self.content = self.content.value
        self.result = self.result.value
        now = datetime.datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')
        try:
            embed = discord.Embed(
                title="バグ報告", description=now)
            embed.add_field(name="コマンド", value=self.select)
            embed.add_field(
                name="ユーザー", value=f"{interaction.user.name}\n{interaction.user.id}")
            embed.add_field(
                name="サーバー", value=f"{interaction.guild.name}\n{interaction.guild.id}")
            embed.add_field(name="\n操作内容", value=self.content)
            embed.add_field(name="詳細", value=f"```{self.result}```")

            channel = await main.sendChannel(1021082211618930801)
            await channel.send(embed=embed)
            embed.title = "不具合を記録しました。"
            embed.description = "ご協力ありがとうございます。\n" + embed.description
            await interaction.edit_original_response(embed=embed, view=None)
            return
        except Exception as e:
            logger.error(f"バグ報告エラー {self.content.value=}, {self.result.value=}, {e=}")
            await interaction.edit_original_response(content="管理者に不具合を通知しました。修正までしばらくお待ちください", view=None)
            raise


class BugSelectView(View):
    @discord.ui.select(
        placeholder="どのコマンドで不具合が出ましたか？",
        options=[
            discord.SelectOption(
                label="/genbot",
                description="help、today等",
            ),
            discord.SelectOption(
                label="/uidlist",
                description="get、controle等",
            ),
            discord.SelectOption(
                label="/genshinstat & /status",
                description="get等",
            ),
            discord.SelectOption(
                label="/wish",
                description="get、get_n等",
            ),
            discord.SelectOption(
                label="/setting",
                description="channel等",
            ),
            discord.SelectOption(
                label="/artifact",
                description="get等",
            ),
            discord.SelectOption(
                label="/notification",
                description="resin等",
            ),
        ],
    )
    async def select_callback(self, select: discord.ui.Select, interaction):
        await interaction.response.send_modal(ReportModal(select.values[0]))


def get_jst(hour: int):
    return (24 - 9 + hour) % 24


class GenbotCog(commands.Cog):

    def __init__(self, bot):
        print('genbot ready')
        self.bot = bot
        getTime.init_reference_times()
        self.day_count.start()

    genbot = SlashCommandGroup('genbot', '今日の日替わり秘境など、便利なコマンドを集めたグループです。')

    @genbot.command(name='help', description='原神ステータスbotに困ったらまずはこれ！')
    async def chelp(self, ctx):
        view = helpselectView(timeout=300, disable_on_timeout=True)
        embed = embeds.Embed(title="確認したいコマンドのジャンルを選択してください。", description="詳しい情報はサポートサーバーから！\nhttps://discord.gg/MxZNQY9CyW")
        await ctx.respond(embed=embed, view=view, ephemeral=sql.Ephemeral.is_ephemeral(ctx.guild.id))

    @genbot.command(name='today', description='今日の日替わり秘境などをまとめて確認！')
    async def today(self, ctx):

        view = weekselectView()
        weekday = view.weekday
        embed = DATA.EMBEDS[weekday].get_embed()
        await ctx.respond(embed=embed, view=view, ephemeral=sql.Ephemeral.is_ephemeral(ctx.guild.id))
        logger.info(f"/genbot today - {weekday}")

    @genbot.command(name='report', description='不具合報告はこちらから！')
    async def report(self, ctx):

        view = BugSelectView()
        embed = embeds.Embed(title="不具合報告", description="サポートサーバーで最新情報を確認することをおすすめします。\nhttps://discord.gg/MxZNQY9CyW")
        await ctx.respond(embed=embed, view=view, ephemeral=sql.Ephemeral.is_ephemeral(ctx.guild.id))
        logger.info(f"/genbot report")

    @genbot.command(name='event', description='開催中のイベントなどをまとめて確認！')
    async def event(self, ctx):
        hoge = await ctx.respond("読み込み中...", ephemeral=sql.Ephemeral.is_ephemeral(ctx.guild.id))
        embed = discord.Embed(title=f"本日開催中のイベントはこちら", color=0x1e90ff)
        event = calendar.get()
        now = "```ありません```"
        before = "```ありません```"
        for i in event:
            if i["start"] > datetime.datetime.now():
                if before == "```ありません```":
                    before = ""
                min = i["start"] - datetime.datetime.now()
                # これで来週の月曜日まであと何分になった
                min = min / datetime.timedelta(minutes=1)
                # これでhourは時間を24で割ったあまりになる
                hour = min/60 % 24
                result = f"{math.floor(min/60/24)}日{math.floor(hour)}時間{math.floor(min % 60)}分"
                before += (f"**イベント名：{i['name']}**\n```css\n{i['description']}\n\n開始まで:{result}\n開始日:{i['start'].strftime('%m月%d日')}\n終了日:{i['end'].strftime('%m月%d日')}```\n")
            else:
                if now == "```ありません```":
                    now = ""
                min = i["end"] - datetime.datetime.now()
                # これで来週の月曜日まであと何分になった
                min = min / datetime.timedelta(minutes=1)
                # これでhourは時間を24で割ったあまりになる
                hour = min/60 % 24
                result = f"{math.floor(min/60/24)}日{math.floor(hour)}時間{math.floor(min % 60)}分"
                now += (f"**イベント名：{i['name']}**\n```css\n{i['description']}\n\n終了日:{i['end'].strftime('%m月%d日')}\n残り時間:{result}```\n")
        embed.add_field(inline=True, name="開催中のイベント\n", value=now)
        embed.add_field(inline=True, name="開催予定のイベント\n", value=before)
        await hoge.edit_original_response(content=None, embed=embed)
        print(f"\n実行者:{ctx.author.name}\n鯖名:{ctx.guild.name}\nevent - イベント確認")

    @genbot.command(name='code', description='報酬コードを取得するためのURLを作成します')
    async def code(self, ctx: discord.ApplicationContext, code: Option(input_type=str, description='報酬コードを入力してください', required=True)):
        embed = embeds.Embed(title="報酬コード", description="以下のリンクから報酬を取得してください。\nhttps://genshin.hoyoverse.com/ja/gift?code=" + code)
        await ctx.respond(embed=embed, ephemeral=sql.Ephemeral.is_ephemeral(ctx.guild.id))
        logger.info(f"/genbot code - {code}")

    @genbot.command(name='dev', description='開発者用コマンドです。')
    async def dev(self, ctx: discord.ApplicationContext,):
        if ctx.author.id == 698127042977333248 or ctx.author.id == 751697679721168986 or ctx.author.id == 802066206529028117:
            await main.reload_cogs()
            await ctx.respond("Cogs reloaded.", ephemeral=sql.Ephemeral.is_ephemeral(ctx.guild.id)) 
        else:
            await ctx.respond("管理者限定コマンドです。", ephemeral=sql.Ephemeral.is_ephemeral(ctx.guild.id))

    @tasks.loop(time=[datetime.time(hour=get_jst(5), second=1), datetime.time(hour=get_jst(1), second=1)])
    async def day_count(self):
        getTime.init_reference_times()
        logger.info("日付が変わりました。")


def setup(bot):
    bot.add_cog(GenbotCog(bot))
