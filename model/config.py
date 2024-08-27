class Help:
    def __init__(self, data) -> None:
        self.name: str = data['name']
        self.emoji: str = data['emoji']
        self.description: str = data['description']

class Config:
    def __init__(self, data) -> None:
        self.version: str = data['VERSION']
        self.debug:  bool = data['DEBUG']
        self.debug_server: str = data['DEBUG_SERVER']
        self.cogs_list: list[str] = data['COGS_LIST']
        self.help_list: list[Help] = [Help(i) for i in data['HELP_LIST']]