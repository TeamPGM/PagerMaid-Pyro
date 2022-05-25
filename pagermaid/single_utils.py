from os import sep, remove, mkdir
from os.path import exists
from typing import List, Optional
from pyrogram.types import Message
from sqlitedict import SqliteDict

# init folders
if not exists("data"):
    mkdir("data")
sqlite = SqliteDict(f"data{sep}data.sqlite", autocommit=True)


def get_sudo_list():
    return sqlite.get("sudo_list", [])


def _status_sudo():
    return sqlite.get("sudo_enable", False)


def safe_remove(name: str) -> None:
    try:
        remove(name)
    except FileNotFoundError:
        pass


class Message(Message):  # noqa
    arguments: str
    parameter: List

    def obtain_message(self) -> Optional[str]:
        """ Obtains a message from either the reply message or command arguments. """
        return

    def obtain_user(self) -> Optional[int]:
        """ Obtains a user from either the reply message or command arguments. """
        return

    async def safe_delete(self, revoke: bool = True) -> None:
        return
