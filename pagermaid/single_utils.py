from os import sep, remove, mkdir
from os.path import exists
from typing import List
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

    async def safe_delete(self, revoke: bool = True):
        try:
            return await self._client.delete_messages(
                chat_id=self.chat.id,
                message_ids=self.id,
                revoke=revoke
            )
        except Exception as e:  # noqa
            return False
