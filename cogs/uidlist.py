import discord
from discord.ui import Select, View, Button, Modal
from discord.ext import commands
from discord import Option, SlashCommandGroup
import aiohttp
import lib.sql as SQL
from lib import enkaconnecter

from repository.config import CONFIG
from repository.icons import Icons
from main import logger
import view.embeds as embeds

l: list[discord.SelectOption] = []

# UIDを聞くモーダル


class UidModal(discord.ui.Modal):
    def __init__(self, ctx):
        super().__init__(title="あなたのUIDを入力してください。", timeout=300,)
        self.ctx = ctx

        self.uid = discord.ui.InputText(
            label="UIDを半角数字で入力してください。",
            style=discord.InputTextStyle.short,
            min_length=9,
            max_length=10,
            required=True,
        )
        self.add_item(self.uid)

    async def callback(self, interaction: discord.Interaction) -> None:
        embed = embeds.LoadingEmbed()
        await interaction.response.edit_message(embed=embed, view=None)
        view = isPablicButton(self.ctx)
        try:
            self.uid = int(self.uid.value)
            is_first_registration = SQL.User.get_user_list(self.ctx.author.id)
            await uid_set(self.ctx, self.uid)
        except Exception as e:
            logger.error(e)
            embed = embeds.ErrorEmbed(description="UIDが無効か、EnkaNetworkがメンテナンス中です。")
            await interaction.edit_original_response(embed=embed, view=None)
            return
        if is_first_registration == []:
            embed = embeds.Embed(description="UIDを登録します。\nUIDを公開すると、UIDリストに表示されるようになります\n※UIDを複数登録している場合は個別で設定することはできません。")
            await interaction.edit_original_response(embed=embed, view=view)
        else:
            embed = await getEmbed(self.ctx)
            await interaction.edit_original_response(content="登録しました！", embed=embed, view=None)
            logger.info(f"/uidlist - UID登録完了")
        return

# 公開するかどうかを聞くボタン


class isPablicButton(View):
    def __init__(self, ctx):
        super().__init__(timeout=300, disable_on_timeout=True)
        self.ctx = ctx

    @discord.ui.button(label="公開する", style=discord.ButtonStyle.green)
    async def callback(self, button, interaction: discord.Interaction):
        embed = embeds.LoadingEmbed()
        await interaction.response.edit_message(embed=embed, view=None)
        SQL.PermitID.add_permit_id(self.ctx.guild.id, self.ctx.author.id)
        embed = await getEmbed(self.ctx)
        await interaction.edit_original_response(content="公開しました。\nUIDは`/uidlist controle`から管理できます。", embed=embed, view=None)
        logger.info(f"/uidlist - 公開")

    @discord.ui.button(label="公開しない", style=discord.ButtonStyle.red)
    async def no_callback(self, button, interaction: discord.Interaction):
        embed = embeds.LoadingEmbed()
        await interaction.response.edit_message(embed=embed, view=None)
        SQL.PermitID.remove_permit_id(self.ctx.guild.id, self.ctx.author.id)
        embed = await getEmbed(self.ctx)
        await interaction.edit_original_response(content="非公開にしました。\nUIDは`/uidlist controle`から管理できます。", embed=embed, view=None)
        logger.info(f"/uidlist - 非公開")

# モーダルを表示させるボタン


class UidModalButton(discord.ui.Button):
    def __init__(self, ctx):
        super().__init__(label="UIDを登録する", style=discord.ButtonStyle.green)
        self.ctx = ctx

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(UidModal(self.ctx))

# UIDを削除するかどうか聞くボタン


class isDeleteButton(discord.ui.Button):
    def __init__(self, ctx, uid):
        super().__init__(label="UIDを削除する", style=discord.ButtonStyle.red)
        self.ctx = ctx
        self.uid = uid

    async def callback(self, interaction: discord.Interaction):
        embed = embeds.Embed(description=f"UIDを登録すれば、各種コマンドの入力が省かれ、便利になります。\n**本当に削除しますか？**\n\n削除しようとしているUID：{self.uid}")
        await interaction.response.edit_message(embed=embed, view=isDeleteEnterButton(self.uid, self.ctx))

# 本当にUIDを削除するかどうか聞くボタン


class isDeleteEnterButton(View):
    def __init__(self, uid: str, ctx):
        super().__init__(timeout=300, disable_on_timeout=True)
        self.ctx = ctx
        self.uid = uid

    @discord.ui.button(label="削除する", style=discord.ButtonStyle.red)
    async def callback(self, button, interaction: discord.Interaction):
        try:
            uid = await uid_del(self.ctx, self.uid)
        except:
            embed = embeds.ErrorEmbed(description=f"{self.uid}を何らかの理由で削除できませんでした。\nよろしければ、botのプロフィールからエラーの報告をお願いします。")
            await interaction.response.edit_message(embed=embed, view=None)
            raise
        self.clear_items()
        embed = embeds.Embed(description=f"UID:{uid}を削除しました。")
        await interaction.response.edit_message(embed=embed, view=self)
        logger.info(f"/uidlist - 削除")

    @discord.ui.button(label="キャンセルする", style=discord.ButtonStyle.green)
    async def no_callback(self, button, interaction: discord.Interaction):
        self.clear_items()
        embed = embeds.Embed(description="削除がキャンセルされました")
        await interaction.response.edit_message(embed=embed, view=self)

# UIDを公開するかどうか聞くボタン


class isPabricEnterButton(discord.ui.Button):
    def __init__(self, ctx):
        super().__init__(label="公開設定変更", style=discord.ButtonStyle.gray)
        self.ctx = ctx

    async def callback(self, interaction: discord.Interaction):
        embed = embeds.Embed(description="UIDを公開すると、UIDリストに表示されるようになります\n※UIDを複数登録している場合は個別で設定することはできません。")
        await interaction.response.edit_message(embed=embed, view=isPablicButton(self.ctx))

# UIDを登録する関数


async def uid_set(ctx, uid):
    resp = await enkaconnecter.get_data(uid)
    print(ctx.guild.name)
    name = resp['playerInfo']['nickname']
    print(name)
    userData = SQL.User(ctx.author.id, uid, name)
    SQL.User.insert_user(userData)
    return

# UIDを削除する関数


async def uid_del(ctx, uid):
    serverId = ctx.guild.id
    SQL.User.delete_user(ctx.author.id, uid)
    return uid


async def getEmbed(ctx):
    serverId = ctx.guild.id
    view = View(timeout=300, disable_on_timeout=True)

    # もしuserに当てはまるUIDが無ければ終了
    uidList = SQL.User.get_user_list(ctx.author.id)
    isPublic = SQL.PermitID.is_user_public(ctx.guild.id, ctx.author.id)
    if isPublic == False:
        isPublic = "非公開です"
    elif isPublic == True:
        isPublic = "公開されています"
    embed = discord.Embed(
        title=f"登録情報",
        description=f"{len(uidList)}個のUIDが登録されています。\n公開設定: {isPublic}",
        color=0x1e90ff,
    )
    for v in uidList:
        embed.add_field(
            inline=False, name=f"ユーザー名・{v.game_name}", value=f"UID: {v.uid}")
    return embed


class select_uid_pulldown(discord.ui.Select):
    def __init__(self, ctx, selectOptions: list[discord.SelectOption], game_name):
        super().__init__(placeholder="削除するUIDを選択してください", options=selectOptions)
        self.ctx = ctx
        self.game_name = game_name

    async def callback(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="削除しようとしているUID", description=f"UID:{self.values[0]}\nユーザー名:{self.game_name}", color=0x1e90ff, )
        await interaction.response.edit_message(content=f"UIDを登録すれば、各種コマンドの入力が省かれ、便利になります。\n**本当に削除しますか？**\n", view=isDeleteEnterButton(int(self.values[0]), self.ctx), embed=embed)
        print(
            f"==========\n実行者:{interaction.user.name}\n鯖名:{interaction.guild.name}\ncontrole - 削除するかどうか")


class uidListCog(commands.Cog):

    def __init__(self, bot):
        print('UidList ready')
        self.bot = bot

    uidlist = SlashCommandGroup('uidlist', 'UIDを管理するコマンドです。')

    @uidlist.command(name="get", description="UIDリストを開きます。")
    async def uidlist_get(
            self,
            ctx: discord.ApplicationContext,
    ):
        embed = embeds.Embed(
            title=f"UIDリスト",
            description="UIDを登録する際に公開設定にするとここに表示されます。",
        )
        uidList = SQL.PermitID.get_uid_list(ctx.guild.id)
        for v in uidList:
            embed.add_field(inline=False, name=v.uid,
                            value=f"Discord： <@{v.d_id}>\nユーザー名：{v.g_name}")
        view = View(timeout=300, disable_on_timeout=True)
        try:
            for v in uidList:
                if v.d_name == ctx.author.name:
                    await ctx.respond(embed=embed, ephemeral=SQL.Ephemeral.is_ephemeral(ctx.guild.id))
                    logger.info(f"/uidlist - 取得")
                    return
        except:
            print(ctx.guild.name)
        button = UidModalButton(ctx)
        view.add_item(button)
        await ctx.respond(embed=embed, view=view, ephemeral=SQL.Ephemeral.is_ephemeral(ctx.guild.id))
        logger.info(f"/uidlist - 取得")

    @uidlist.command(name="control", description="登録したUIDの操作パネルを開きます。")
    async def uidlist_control(
            self,
            ctx: discord.ApplicationContext,
    ):
        try:
            embed = await getEmbed(ctx)
            select_options: list[discord.SelectOption] = []
            userData = SQL.User.get_user_list(ctx.author.id)
            if userData == []:
                view = View(timeout=300, disable_on_timeout=True)
                button = UidModalButton(ctx)
                view.add_item(button)
                await ctx.respond(content="UIDが登録されていません。下のボタンから登録してください。", view=view, ephemeral=True)
                return
            for v in userData:
                select_options.append(
                    discord.SelectOption(label=v.game_name, description=str(v.uid), value=str(v.uid)))
            view = View(timeout=300, disable_on_timeout=True)
            view.add_item(select_uid_pulldown(
                ctx, select_options, v.game_name))
            view.add_item(isPabricEnterButton(ctx))
            view.add_item(UidModalButton(ctx))
            await ctx.respond(embed=embed, view=view, ephemeral=True)
            logger.info(f"/uidlist - 操作")
        except:
            view = View()
            button = UidModalButton(ctx)
            view.add_item(button)
            await ctx.respond(content="UIDが登録されていません。下のボタンから登録してください。", view=view, ephemeral=True)
            print(
            return


def setup(bot):
    bot.add_cog(uidListCog(bot))
