import contextlib
from os import sep, remove, mkdir
from os.path import exists
from typing import List, Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from httpx import AsyncClient

from pyrogram import Client
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
    with contextlib.suppress(FileNotFoundError):
        remove(name)


class Client(Client):  # noqa
    job: Optional[AsyncIOScheduler] = None


class Message(Message):  # noqa
    arguments: str
    parameter: List
    bot: Client
    request: Optional[AsyncClient] = None

    def obtain_message(self) -> Optional[str]:
        """ Obtains a message from either the reply message or command arguments. """
        return

    def obtain_user(self) -> Optional[int]:
        """ Obtains a user from either the reply message or command arguments. """
        return

    async def delay_delete(self, delete_seconds: int = 60) -> Optional[bool]:
        return

    async def safe_delete(self, revoke: bool = True) -> None:
        return
