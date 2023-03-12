from os import sep
from json import dump as json_dump
from typing import List, Dict

from pydantic import BaseModel

from pagermaid.common.reload import reload_all
from pagermaid.config import Config


class Alias(BaseModel):
    command: str
    alias: str


class AliasManager:
    def __init__(self):
        self.alias_list = []
        for key, value in Config.alias_dict.items():
            temp = Alias(command=key, alias=value)
            self.alias_list.append(temp)

    def get_all_alias(self):
        return self.alias_list

    def get_all_alias_dict(self):
        return [i.dict() for i in self.alias_list]

    def get_all_alias_text(self) -> str:
        texts = []
        texts.extend(f"`{i.command}` > `{i.alias}`" for i in self.alias_list)
        return "\n".join(texts)

    @staticmethod
    def save():
        with open(f"data{sep}alias.json", "w", encoding="utf-8") as f:
            json_dump(Config.alias_dict, f)

    @staticmethod
    def delete_alias(source_command: str):
        del Config.alias_dict[source_command]
        AliasManager.save()

    @staticmethod
    def add_alias(source_command: str, to_command: str):
        Config.alias_dict[source_command] = to_command
        AliasManager.save()

    @staticmethod
    async def save_from_web(data: List[Dict]):
        Config.alias_dict.clear()
        for i in data:
            temp = Alias(**i)
            Config.alias_dict[temp.command] = temp.alias
        AliasManager.save()
        await reload_all()

    def test_alias(self, message: str) -> str:
        r = message.split(" ")
        for i in self.alias_list:
            if i.command == r[0]:
                r[0] = i.alias
                break
        return " ".join(r)
