from os import sep, remove
from typing import List
from pyrogram.types import Message
from sqlitedict import SqliteDict

sqlite = SqliteDict(f"data{sep}data.sqlite", autocommit=True)


def get_sudo_list():
    return sqlite.get("sudo_list", [])


def get_sudo_level():
    return sqlite.get("sudo_level", {})


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
                message_ids=self.message_id,
                revoke=revoke
            )
        except Exception as e:  # noqa
            return False
