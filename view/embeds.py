import discord
from discord.ui import Select, View, Button
from discord.ext import commands, tasks
from repository.icons import Icons

class Embed(discord.Embed):
    def __init__(
            self, 
            color=0xdaa839, 
            title: str = None, 
            url: str = None, 
            description: str = None,
            ):
        super().__init__(color=color, title=title, url=url, description=description)

class ErrorEmbed(Embed):
    def __init__(
            self, 
            color=0xff4163, 
            title: str = None, 
            url: str = None, 
            description: str = None,
            ):
        super().__init__(color=color, title=title, url=url, description=description)

class LoadingEmbed(Embed):
    def __init__(
            self, 
            color=0xff4163, 
            title: str = f"{Icons.tools.LOADING} 読み込み中...", 
            url: str = None, 
            description: str = None,
            ):
        super().__init__(color=color, title=title, url=url, description=description)