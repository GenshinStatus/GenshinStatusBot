import aiohttp
from lib.yamlutil import yaml
from lib.genshin_status_api import name_to_id, api_connect_ranking_image
from typing import Optional
import json

API_URL_BASE = "https://api.ranking.genst.cinnamon.works"

class SortType:
    ALL = "all"
    CONSTELLATIONS = "constellations"
    LEVEL = "level"
    HP = "added_hp"
    ATK = "added_attack"
    DEF = "added_defense"
    CRIT_RATE = "critical_rate"
    CRIT_DMG = "critical_damage"
    CHARGE = "charge_efficiency"
    ELEMENTAL_MASTERY = "elemental_mastery"
    ELEMENTAL_VALUE = "elemental_value"

class Artifact:
    def __init__(
            self, 
            icon_name: str,
            main_name: str,
            score: float,
        ):
        self.icon_name = icon_name
        self.main_name = main_name
        self.score = score

class Skill:
    def __init__(self, level: int, add_level: int):
        self.level = level
        self.add_level = add_level

class Character:
    def __init__(
            self,
            id: str,
            level: int,
            constellation: int,
            hp: int,
            attack: int,
            defense: int,
            critical_rate: float,
            critical_damage: float,
            charge_efficiency: float,
            elemental_mastery: int,
            elemental_name: str,
            elemental_value: int,
            skills: list[Skill],
            artifacts: dict[str, Artifact],
        ):
        self.id = id
        self.level = level
        self.constellation = constellation
        self.hp = hp
        self.attack = attack
        self.defense = defense
        self.critical_rate = critical_rate
        self.critical_damage = critical_damage
        self.charge_efficiency = charge_efficiency
        self.elemental_mastery = elemental_mastery
        self.elemental_name = elemental_name
        self.elemental_value = elemental_value
        self.skills = skills
        self.artifacts = artifacts

class Ranking:
    def __init__(
            self, 
            rank: int,
            uid: int,
            level: int,
            nickname: str,
            character: Character,
        ):
        self.uid = uid
        self.rank = rank
        self.level = level
        self.nickname = nickname
        self.character = character
    
    async def get_rankings_image(self):
        return api_connect_ranking_image(json.dumps(self))

class Rankings:
    def __init__(self, rankings: list[Ranking]):
        self.rankings = rankings

    async def get_rankings_image(self):
        pass
        
async def post_write(uid, name):
    """データを登録します
    """
    character_id = name_to_id(name)
    url = f"{API_URL_BASE}/api/write/{uid}/{character_id}"
    async with aiohttp.ClientSession(raise_for_status=True) as session:
        async with session.get(url) as response:
            resp = await response.json()

    if resp["status"] == "success":
        return
    else:
        raise Exception("Ranking write error")
    
async def get_view(uid, sortkey: Optional[SortType], character: Optional[str]) -> dict:
    """uidのランキングを取得します

    Args:
        sortkey (SortType): ソートキー
        character (str): キャラクターID

    Returns:
        dict: APIから取得したjsonをdictに変換したもの
    """
    url = f"{API_URL_BASE}/api/view/{uid}"

    params = {}
    if sortkey:params["sort"] = sortkey
    if character:params["character"] = character
    if params:url += "?" + "&".join([f"{key}={value}" for key, value in params.items()])

    async with aiohttp.ClientSession(raise_for_status=True) as session:
        async with session.get(url) as response:
            resp = await response.json()
    return resp

async def get_ranking(sortkey: Optional[SortType], character: Optional[str]) -> dict:
    """ランキングを取得します

    Args:
        sortkey (SortType): ソートキー
        character (str): キャラクターID

    Returns:
        dict: APIから取得したjsonをdictに変換したもの
    """
    url = f"{API_URL_BASE}/api/ranking"

    params = {}
    if sortkey:params["sort"] = sortkey
    if character:params["character"] = character
    if params:url += "?" + "&".join([f"{key}={value}" for key, value in params.items()])

    async with aiohttp.ClientSession(raise_for_status=True) as session:
        async with session.get(url) as response:
            resp = await response.json()
    return resp

async def delete_user(uid):
    """ユーザーを削除します
    """
    url = f"{API_URL_BASE}/api/delete/{uid}"
    async with aiohttp.ClientSession(raise_for_status=True) as session:
        async with session.get(url) as response:
            resp = await response.json()

    if resp["status"] == "success":
        return
    else:
        raise Exception("Ranking delete error")