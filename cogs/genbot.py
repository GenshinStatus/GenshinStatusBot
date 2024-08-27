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
        embed = discord.Embed(
            title=f"helpコマンド：{select.values[0]}", color=0x1e90ff)
        if select.values[0] == "メインコマンド":
            print(
                f"help - メインコマンド\n実行者:{interaction.user.name}\n鯖名:{interaction.guild.name}")
            embed.add_field(
                name=f"このbotのメインとなるコマンドです。",
                value=f"\
                    \n**・/genshinstat get**\nプロフィール画像とキャラのビルド画像を作成します。UIDリスト機能で、自分のUIDを登録しておくと簡単に使えます。\
                    \n**・/status**\n/genshinstat getのコマンド名を短縮したものです。機能は全く同じです。\
                ")
        elif select.values[0] == "UIDリストコマンド":
            print(
                f"help - UIDリストコマンド\n実行者:{interaction.user.name}\n鯖名:{interaction.guild.name}")
            embed.add_field(
                name=f"UIDを管理するコマンドです。",
                value=f"\
                    \n**・/uidlist get**\n登録され、公開設定が「公開」になっているUIDがここに表示されます。\
                    \n**・/uidlist control**\n登録したUIDを管理するパネルを表示します。UIDの登録や削除、公開設定の切り替えもここからできます。\
                ")
        elif select.values[0] == "祈願コマンド":
            print(
                f"help - 祈願コマンド\n実行者:{interaction.user.name}\n鯖名:{interaction.guild.name}")
            embed.add_field(
                name=f"いわゆるガチャシミュレーターです。天井もユーザーごとにカウントされています。",
                value=f"\
                    \n**・/wish character**\n原神のガチャ排出時に表示されるイラストを検索します。\
                    \n**・/wish get**\n原神のガチャを引きます。\
                    "
            )
        elif select.values[0] == "便利コマンド":
            print(
                f"help - 便利コマンド\n実行者:{interaction.user.name}\n鯖名:{interaction.guild.name}")
            embed.add_field(
                name=f"botを活用する上で覚えておきたいコマンドたちです。",
                value=f"\
                    \n**・/genbot help**\n迷ったらこちらから確認しよう。\
                    \n**・/genbot today**\n今日の日替わり秘境（天賦本や武器突破素材）や、デイリー更新まであと何分？を表示！\
                    \n**・/genbot report**\nバグ・不具合報告はこちらからよろしくお願いいたします...\
                    \n**・/genbot event**\n原神のイベントを確認できます。\
                    \n**・/genbot code**\nワンボタンで原神報酬コードを使いたい方にどうぞっ！\
                ")
        elif select.values[0] == "聖遺物スコア計算コマンド":
            print(
                f"help - 聖遺物スコア計算コマンド\n実行者:{interaction.user.name}\n鯖名:{interaction.guild.name}")
            embed.add_field(
                name=f"聖遺物スコア計算を簡単にしてくれるコマンドです。",
                value=f"\
                    \n**・/artifact get**\n会心率基準で簡単に計算してくれます。数値はコマンド実行時に入力します。\
                    \n**・/artifact get_detail**\nHP基準や防御力基準など、より詳細に設定して計算します。\
                ")
        elif select.values[0] == "通知コマンド":
            print(
                f"help - 通知コマンド\n実行者:{interaction.user.name}\n鯖名:{interaction.guild.name}")
            embed.add_field(
                name=f"樹脂が溢れないように通知してくれるコマンドです。",
                value=f"\
                    \n**・/notification resin**\n現在の樹脂量を入力することで、溢れる前に通知します。\
                ")
        elif select.values[0] == "設定コマンド":
            print(
                f"help - 設定コマンド\n実行者:{interaction.user.name}\n鯖名:{interaction.guild.name}")
            embed.add_field(
                name=f"各種設定するコマンドです。サーバー管理者限定です。",
                value=f"\
                    \n**・/setting channel**\n樹脂通知をするチャンネルを設定します。\
                    \n**・/setting ephemeral**\nコマンドの実行履歴が他人に表示させるか選択します。ビルド画像などを共有したい場合はオンにしてください。\
                ")
        await interaction.response.edit_message(content=None, embed=embed, view=self)


class MyEmbed(discord.Embed):
    def __init__(self, day_of_week: str, url: str):
        super().__init__(title=f"{day_of_week}の日替わり秘境はこちら", color=0x1e90ff)
        self.set_image(url=url)

    def get_embed(self):
        embed = copy.deepcopy(self)

        now = datetime.datetime.now()
        # 明日の5時
        daily = int(getTime.daily.timestamp() - time.time())
        resalt = f"約{daily//3600}時間{daily%3600//60}分"
        embed.add_field(inline=False, name="デイリー更新まで",
                        value=f"```fix\nあと{resalt}```")
        # 明日の1時
        hoyo = int(getTime.hoyo.timestamp() - time.time())
        resalt = f"約{hoyo//3600}時間{hoyo%3600//60}分"
        embed.add_field(inline=False, name="HoYoLabログインボーナス更新まで",
                        value=f"ログインボーナス：https://t.co/MnjUZfg7Dn\n```fix\nあと{resalt}```")
        # 曜日取得
        weekly = int(getTime.weekly.timestamp() - time.time())
        resalt = f"約{weekly//86400}日{weekly%86400//3600}時間{weekly%86400%3600//60}分"
        embed.add_field(inline=False, name="週ボス等リセットまで",
                        value=f"```fix\nあと{resalt}```")
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
        embed = MyEmbed(day_of_week=day_of_week, url=url)
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

    @discord.ui.button(label="次の日の秘境")
    async def nextday(self, _: discord.ui.Button, interaction: discord.Interaction):
        self.weekday = (self.weekday + 1) % 7
        await interaction.response.edit_message(embed=DATA.EMBEDS[self.weekday].get_embed(), view=self)

    @discord.ui.select(
        placeholder="確認したい曜日を選択",
        options=DATA.SELECT_OPTIONS
    )
    async def select_callback(self, select: discord.ui.Select, interaction: discord.Interaction):
        self.weekday = int(select.values[0])
        view = self
        print(
            f"実行者:{interaction.user.name}\n鯖名:{interaction.guild.name}\n日替わり - {self.weekday}")
        await interaction.response.edit_message(embed=DATA.EMBEDS[self.weekday].get_embed(), view=view)

# バグ報告モーダル


class ReportModal(discord.ui.Modal):
    def __init__(self, select: str):
        super().__init__(title="バグ報告", timeout=300,)
        self.select = select

        self.content = discord.ui.InputText(
            label="バグの内容",
            style=discord.InputTextStyle.paragraph,
            placeholder="どのような状況でしたか？",
            required=True,
        )
        self.add_item(self.content)
        self.resalt = discord.ui.InputText(
            label="バグによって生じたこと",
            style=discord.InputTextStyle.paragraph,
            placeholder="例：インタラクションに失敗した、メッセージが大量に表示された等",
            required=True,
        )
        self.add_item(self.resalt)

    async def callback(self, interaction: discord.Interaction) -> None:
        await interaction.response.edit_message(content="読み込み中...")
        self.content = self.content.value
        self.resalt = self.resalt.value
        now = datetime.datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')
        try:
            embed = discord.Embed(
                title=f"バグ報告", color=0x1e90ff, description=now)
            embed.add_field(name="コマンド", value=self.select)
            embed.add_field(
                name="ユーザー", value=f"{interaction.user.name}\n{interaction.user.id}")
            embed.add_field(
                name="サーバー", value=f"{interaction.guild.name}\n{interaction.guild.id}")
            embed.add_field(name="\n内容", value=self.content)
            embed.add_field(name="詳細", value=f"```{self.resalt}```")

            channel = await main.sendChannel(1021082211618930801)
            await channel.send(embed=embed)
            await interaction.edit_original_response(content=f"不具合を送信しました！ご協力ありがとうございます！\nbugTrackName:{self.content}", view=None)
            return
        except:
            print("おい管理者！エラーでてんぞこの野郎！！！！")
            await interaction.edit_original_response(content=f"送信できませんでしたが、管理者にログを表示しました。修正までしばらくお待ちください", view=None)
            raise


class bugselectView(View):
    @discord.ui.select(
        placeholder="どのコマンドで不具合が出ましたか？",
        options=[
            discord.SelectOption(
                    label="/genbot",
                    description="help、today等",),
            discord.SelectOption(
                label="/uidlist",
                description="get、controle等",),
            discord.SelectOption(
                label="/genshinstat & /status",
                description="get等"),
            discord.SelectOption(
                label="/wish",
                description="get、get_n等"),
            discord.SelectOption(
                label="/setting",
                description="channel等"),
            discord.SelectOption(
                label="/artifact",
                description="get等"),
            discord.SelectOption(
                label="/notification",
                description="resin等"),
        ])
    async def select_callback(self, select: discord.ui.Select, interaction):
        print(str(select.values[0]))
        await interaction.response.send_modal(ReportModal(select.values[0]))


def get_jst(hour: int):
    return (24 - 9 + hour) % 24


class GenbotCog(commands.Cog):

    def __init__(self, bot):
        print('genbot_initしたよ')
        self.bot = bot
        getTime.init_reference_times()
        print(
            f'＝＝＝＝＝＝＝＝＝＝＝＝＝日付を更新したんご＝＝＝＝＝＝＝＝＝＝＝＝＝\n{datetime.datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")}')
        self.slow_count.start()

    genbot = SlashCommandGroup('genbot', 'test')

    @genbot.command(name='help', description='原神ステータスbotに困ったらまずはこれ！')
    async def chelp(self, ctx):
        view = helpselectView(timeout=300, disable_on_timeout=True)
        # レスポンスで定義したボタンを返す
        await ctx.respond("**確認したいコマンドのジャンルを選択してね**\n詳しい情報はサポートサーバーから！\nhttps://discord.gg/MxZNQY9CyW", view=view, ephemeral=sql.Ephemeral.is_ephemeral(ctx.guild.id))

    @genbot.command(name='today', description='今日の日替わり秘境などをまとめて確認！')
    async def today(self, ctx):

        view = weekselectView()
        weekday = view.weekday
        embed = DATA.EMBEDS[weekday].get_embed()
        await ctx.respond(embed=embed, view=view, ephemeral=sql.Ephemeral.is_ephemeral(ctx.guild.id))
        print(
            f"\n実行者:{ctx.author.name}\n鯖名:{ctx.guild.name}\ntoday - 今日の日替わり秘境")

    @genbot.command(name='report', description='不具合報告はこちらから！')
    async def report(self, ctx):

        view = bugselectView()
        await ctx.respond(content="報告前にサポートサーバーで最新情報を確認することをおすすめします。\nhttps://discord.gg/MxZNQY9CyW", view=view, ephemeral=sql.Ephemeral.is_ephemeral(ctx.guild.id))
        print(f"\n実行者:{ctx.author.name}\n鯖名:{ctx.guild.name}\nreport - 不具合報告")

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
                resalt = f"{math.floor(min/60/24)}日{math.floor(hour)}時間{math.floor(min % 60)}分"
                before += (f"**イベント名：{i['name']}**\n```css\n{i['description']}\n\n開始まで:{resalt}\n開始日:{i['start'].strftime('%m月%d日')}\n終了日:{i['end'].strftime('%m月%d日')}```\n")
            else:
                if now == "```ありません```":
                    now = ""
                min = i["end"] - datetime.datetime.now()
                # これで来週の月曜日まであと何分になった
                min = min / datetime.timedelta(minutes=1)
                # これでhourは時間を24で割ったあまりになる
                hour = min/60 % 24
                resalt = f"{math.floor(min/60/24)}日{math.floor(hour)}時間{math.floor(min % 60)}分"
                now += (f"**イベント名：{i['name']}**\n```css\n{i['description']}\n\n終了日:{i['end'].strftime('%m月%d日')}\n残り時間:{resalt}```\n")
        embed.add_field(inline=True, name="開催中のイベント\n", value=now)
        embed.add_field(inline=True, name="開催予定のイベント\n", value=before)
        await hoge.edit_original_response(content=None, embed=embed)
        print(f"\n実行者:{ctx.author.name}\n鯖名:{ctx.guild.name}\nevent - イベント確認")

    @genbot.command(name='code', description='報酬コードがすでに入力された状態のURLを作成します')
    async def code(self, ctx: discord.ApplicationContext, code: Option(input_type=str, description='報酬コードを入力してください', required=True)):
        await ctx.respond(f"以下のリンクから報酬を取得してください。\nhttps://genshin.hoyoverse.com/ja/gift?code={code}", ephemeral=sql.Ephemeral.is_ephemeral(ctx.guild.id))
        print(f"\n実行者:{ctx.author.name}\n鯖名:{ctx.guild.name}\ncode - コード生成")

    @genbot.command(name='dev', description='開発者用コマンドです。')
    async def dev(self, ctx: discord.ApplicationContext,):
        if ctx.author.id == 698127042977333248 or ctx.author.id == 751697679721168986 or ctx.author.id == 802066206529028117:
            await main.reload_cogs()
            await ctx.respond("Cogs reloaded.", ephemeral=sql.Ephemeral.is_ephemeral(ctx.guild.id)) 
        else:
            await ctx.respond("管理者限定コマンドです。", ephemeral=sql.Ephemeral.is_ephemeral(ctx.guild.id))

    @tasks.loop(time=[datetime.time(hour=get_jst(5), second=1), datetime.time(hour=get_jst(1), second=1)])
    async def slow_count(self):
        getTime.init_reference_times()
        print(
            f'＝＝＝＝＝＝＝＝＝＝＝＝＝日付を更新したんご＝＝＝＝＝＝＝＝＝＝＝＝＝\n{datetime.datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")}')


def setup(bot):
    bot.add_cog(GenbotCog(bot))
