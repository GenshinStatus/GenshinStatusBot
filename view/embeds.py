import discord
from discord.ui import Select, View, Button
from discord.ext import commands, tasks

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