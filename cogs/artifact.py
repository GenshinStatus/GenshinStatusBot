import discord
from discord.ui import Select, View
from discord.ext import commands, tasks
from discord.commands import Option, OptionChoice, SlashCommandGroup
from repository.icons import Icons
from main import logger
import view.embeds as embeds

import lib.sql as sql

MAIN_OPTION = {
    "花": ["HP"],
    "羽": ["攻撃力"],
    "時計": ["HP%", "攻撃力%", "防御力%", "元素熟知", "元素チャージ効率"],
    "杯": ["HP%", "攻撃力%", "防御力%", "元素熟知", "元素ダメージ"],
    "冠": ["HP%", "攻撃力%", "防御力%", "元素熟知", "与える治癒効果", "会心率", "会心ダメージ"]
}

SUB_OPTION = [
    "攻撃力",
    "攻撃力%",
    "防御力",
    "防御力%",
    "HP",
    "HP%",
    "元素熟知",
    "元素チャージ効率",
    "会心率",
    "会心ダメージ"
]

class ArtifactBaseSelectView(View):

    @discord.ui.select(
        placeholder="聖遺物タイプ",
        options=[
            discord.SelectOption(
                    label="花",
                    description="HP",),
            discord.SelectOption(
                label="羽",
                description="攻撃力",),
            discord.SelectOption(
                label="時計",
                description="、".join(MAIN_OPTION["時計"])),
            discord.SelectOption(
                label="杯",
                description="、".join(MAIN_OPTION["杯"])),
            discord.SelectOption(
                label="冠",
                description="、".join(MAIN_OPTION["冠"])),
        ])
    async def select_callback(self, select: discord.ui.Select, interaction: discord.Interaction):
        view = View()
        view.add_item(ArtifactSuboptionSelect(select.values[0]))
        await interaction.response.edit_message(content="サブオプションを選択してください", view=view)


class ArtifactSuboptionSelect(discord.ui.Select):
    def __init__(self, mainType: str):
        self.listSubOption: list[discord.SelectOption] = []
        self.mainType = mainType
        for v in SUB_OPTION:
            self.listSubOption.append(discord.SelectOption(label=v))
        super().__init__(placeholder="サブオプションを選択（最大4つ）",
                         max_values=4, options=self.listSubOption)

    async def callback(self, interaction: discord.Interaction):
        resalt = []
        for n in self.values:
            resalt.append(n)
        await interaction.response.send_modal(ArtifactSuboptionValueModal(resalt, self.mainType))


class ArtifactSuboptionValueModal(discord.ui.Modal):
    def __init__(self, lst: list, mainType: str):
        super().__init__(title="数値入力（半角数字で小数点まで入力してください）", timeout=300)
        self.lst = lst
        self.mainType = mainType
        self.contents = []

        for i, option in enumerate(lst[:4]):
            content = discord.ui.InputText(
                label=f"{option}（半角数字で小数点まで入力してください）",
                style=discord.InputTextStyle.short,
                placeholder=f"{option}の数値",
                required=True
            )
            self.contents.append(content)
            self.add_item(content)

    async def callback(self, interaction: discord.Interaction) -> None:
        resalt = {}
        for i, option in enumerate(self.lst[:4]):
            try:
                resalt[option] = self.contents[i].value
            except:
                pass
        view = View()
        view.add_item(ArtifactScoreSelectView(resalt, self.mainType))
        await interaction.response.edit_message(content="スコア計算方法", view=view)


# スコア計算方法を選択
class ArtifactScoreSelectView(discord.ui.Select):

    def __init__(self, resaltDict: dict, mainType: str):
        self.listScoreOption: list[discord.SelectOption] = []
        self.mainType = mainType
        self.subDict = resaltDict
        self.listScoreOption: list[discord.SelectOption] = [
            discord.SelectOption(
            label="会心ビルド",
            description="攻撃力%+会心率×2+会心ダメージ"
            ),
            discord.SelectOption(
            label="HPビルド",
            description="HP%+会心率×2+会心ダメージ"
            ),
            discord.SelectOption(
            label="防御力ビルド",
            description="防御力%+会心率×2+会心ダメージ"
            ),
            discord.SelectOption(
            label="元素チャージビルド",
            description="元素チャージ効率×0.9+会心率×2+会心ダメージ"
            ),
            discord.SelectOption(
            label="元素熟知ビルド",
            description="元素熟知×0.25+会心率×2+会心ダメージ"
            )
        ]
        super().__init__(placeholder="スコア計算方法を選択", options=self.listScoreOption)

    async def callback(self, interaction: discord.Interaction):
        try:
            attack = 0
            rate = 0
            damage = 0
            hp = 0
            defence = 0
            cherge = 0
            mastery = 0

            for k, v in self.subDict.items():
                if k == "攻撃力%":
                    attack = v
                elif k == "会心率":
                    rate = v
                elif k == "会心ダメージ":
                    damage = v
                elif k == "HP%":
                    hp = v
                elif k == "防御力%":
                    defence = v
                elif k == "元素チャージ効率":
                    cherge = v
                elif k == "元素熟知":
                    mastery = v

            if self.values[0] == "会心ビルド":
                resalt = float(attack) + float(rate) * 2 + float(damage)
            elif self.values[0] == "HPビルド":
                resalt = float(hp) + float(rate) * 2 + float(damage)
            elif self.values[0] == "防御力ビルド":
                resalt = float(defence) + float(rate) * 2 + float(damage)
            elif self.values[0] == "元素チャージビルド":
                resalt = float(cherge) * 0.9 + float(rate) * 2 + float(damage)
            elif self.values[0] == "元素熟知ビルド":
                resalt = float(mastery) * 0.25 + float(rate) * 2 + float(damage)
        except:
            await interaction.response.edit_message(content="エラー：入力された数値が正しくない数値だった可能性があります。数値は半角英数字で小数点第一位まで記入してください。", view=None, embed=None)
            logger.info(f"artifact_get - 無効な数値")
            return
        embed = embeds.Embed(title="聖遺物スコア計算結果", description=f"{self.values[0]}\n**"+str(round(resalt, 1))+"**")
        await interaction.response.edit_message(content=None, view=None, embed=embed)

class ArtifactCog(commands.Cog):

    def __init__(self, bot):
        logger.info('ArtifacterCog ready')
        self.bot = bot

    artifact = SlashCommandGroup('artifact', '聖遺物スコアを数値から算出します。')

    @artifact.command(name='get_detail', description='より詳細に聖遺物スコアを計算します。')
    async def get_detail(self, ctx: discord.ApplicationContext,):
        await ctx.respond(content="聖遺物のタイプを選択してください。", view=ArtifactBaseSelectView(), ephemeral=sql.Ephemeral.is_ephemeral(ctx.guild.id))
        logger.info(f"/artifact_get_detail")

    @artifact.command(name='get', description='会心基準で手軽に聖遺物スコアを計算します。')
    async def get(
        self,
        ctx: discord.ApplicationContext,
        damage: Option(float, required=False, description="攻撃力%"), # type: ignore
        crper: Option(float, required=False, description="会心率"), # type: ignore
        crdamage: Option(float, required=False, description="会心ダメージ") # type: ignore
    ):
        logger.info(f"/artifact_get")

        damage = float(damage) if damage else 0
        crper = float(crper) if crper else 0
        crdamage = float(crdamage) if crdamage else 0

        try:
            resalt = damage + crper * 2 + crdamage
        except ValueError:
            await ctx.respond(content="有効な数値を入力してください", ephemeral=sql.Ephemeral.is_ephemeral(ctx.guild.id))
            logger.info(f"artifact_get - 無効な数値: {damage=}, {crper=}, {crdamage=}")
            return
        embed = embeds.Embed(title=f"{Icons.stauts.CRITICAL_HURT} {Icons.props.Star} 聖遺物スコア 計算結果", description="会心基準ビルド\n**"+str(round(resalt, 1))+"**")
        embed.set_footer(
            text="HP基準計算など、他の計算方式を使う場合は /artifact get_detail を使用してください。")
        await ctx.respond(embed=embed, ephemeral=sql.Ephemeral.is_ephemeral(ctx.guild.id))


def setup(bot):
    bot.add_cog(ArtifactCog(bot))
