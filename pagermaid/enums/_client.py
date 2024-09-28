from typing import List, Optional, Union
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from pyrogram import Client as OldClient
from pyrogram.types import Chat as OldChat, Message as OldMessage, Dialog

from pyromod.utils.conversation import Conversation


class Message(OldMessage):
    arguments: str
    parameter: List
    forum_topic: Optional[bool] = None
    chat: "Chat"

    def obtain_message(self) -> Optional[str]:
        """Obtains a message from either the reply message or command arguments."""

    def obtain_user(self) -> Optional[int]:
        """Obtains a user from either the reply message or command arguments."""

    async def delay_delete(self, delay: int = 60) -> Optional[bool]:
        """Deletes the message after a specified amount of seconds."""

    async def safe_delete(self, revoke: bool = True) -> None:
        """Safely deletes the message."""


class Client(OldClient):
    job: Optional[AsyncIOScheduler] = None

    async def listen(self, chat_id, filters=None, timeout=None) -> Optional[Message]:
        """Listen for a message in a conversation."""

    async def ask(
        self, chat_id, text, filters=None, timeout=None, *args, **kwargs
    ) -> Optional[Message]:
        """Ask a message in a conversation."""

    def cancel_listener(self, chat_id):
        """Cancel the conversation with the given chat_id."""

    def cancel_all_listeners(self):
        """Cancel all conversations."""

    def conversation(
        self, chat_id: Union[int, str], once_timeout: int = 60, filters=None
    ) -> Optional[Conversation]:
        """Initialize a conversation with the given chat_id."""

    async def get_dialogs_list(self) -> List[Dialog]:
        """Get a list of all dialogs."""


class Chat(OldChat):
    is_forum: Optional[bool] = None

    async def listen(self, chat_id, filters=None, timeout=None) -> Optional[Message]:
        """Listen for a message in a conversation."""

    async def ask(
        self, chat_id, text, filters=None, timeout=None, *args, **kwargs
    ) -> Optional[Message]:
        """Ask a message in a conversation."""

    def cancel_listener(self, chat_id):
        """Cancel the conversation with the given chat_id."""
