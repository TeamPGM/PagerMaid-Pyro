from typing import List
from pagermaid.single_utils import sqlite


class Sub:
    def __init__(self, name: str):
        self.name = name

    def get_subs(self) -> List:
        return sqlite.get(f"{self.name}.sub", [])

    def clear_subs(self) -> None:
        sqlite[f"{self.name}.sub"] = []
        del sqlite[f"{self.name}.sub"]

    def add_id(self, uid: int) -> bool:
        data = self.get_subs()
        if uid in data:
            return False
        data.append(uid)
        sqlite[f"{self.name}.sub"] = data
        return True

    def del_id(self, uid: int) -> bool:
        data = self.get_subs()
        if uid not in data:
            return False
        data.remove(uid)
        sqlite[f"{self.name}.sub"] = data
        return True

    def check_id(self, uid: int) -> bool:
        data = self.get_subs()
        return uid in data
