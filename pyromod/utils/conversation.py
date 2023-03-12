import asyncio
import functools
from typing import Union
from pyrogram.raw.types import InputPeerUser, InputPeerChat, InputPeerChannel
from pyromod.utils.errors import AlreadyInConversationError


def _checks_cancelled(f):
    @functools.wraps(f)
    def wrapper(self, *args, **kwargs):
        if self._cancelled:
            raise asyncio.CancelledError("The conversation was cancelled before")

        return f(self, *args, **kwargs)

    return wrapper


class Conversation:
    def __init__(
        self, client, chat_id: Union[int, str], once_timeout: int = 60, filters=None
    ):
        self._client = client
        self._chat_id = chat_id
        self._once_timeout = once_timeout
        self._filters = filters
        self._cancelled = False

    @_checks_cancelled
    async def send_message(self, *args, **kwargs):
        return await self._client.send_message(self._chat_id, *args, **kwargs)

    @_checks_cancelled
    async def send_media_group(self, *args, **kwargs):
        return await self._client.send_media_group(self._chat_id, *args, **kwargs)

    @_checks_cancelled
    async def send_photo(self, *args, **kwargs):
        return await self._client.send_photo(self._chat_id, *args, **kwargs)

    @_checks_cancelled
    async def send_document(self, *args, **kwargs):
        return await self._client.send_document(self._chat_id, *args, **kwargs)

    @_checks_cancelled
    async def send_sticker(self, *args, **kwargs):
        return await self._client.send_sticker(self._chat_id, *args, **kwargs)

    @_checks_cancelled
    async def send_voice(self, *args, **kwargs):
        return await self._client.send_voice(self._chat_id, *args, **kwargs)

    @_checks_cancelled
    async def send_video(self, *args, **kwargs):
        return await self._client.send_video(self._chat_id, *args, **kwargs)

    @_checks_cancelled
    async def ask(self, text, filters=None, timeout=None, *args, **kwargs):
        filters = filters or self._filters
        timeout = timeout or self._once_timeout
        return await self._client.ask(
            self._chat_id, text, filters=filters, timeout=timeout, *args, **kwargs
        )

    @_checks_cancelled
    async def get_response(self, filters=None, timeout=None):
        filters = filters or self._filters
        timeout = timeout or self._once_timeout
        return await self._client.listen(self._chat_id, filters, timeout)

    def mark_as_read(self, message=None):
        return self._client.read_chat_history(
            self._chat_id, max_id=message.id if message else 0
        )

    def cancel(self):
        self._cancelled = True
        self._client.cancel_listener(self._chat_id)

    async def __aenter__(self):
        self._peer_chat = await self._client.resolve_peer(self._chat_id)
        if isinstance(self._peer_chat, InputPeerUser):
            self._chat_id = self._peer_chat.user_id
        elif isinstance(self._peer_chat, InputPeerChat):
            self._chat_id = self._peer_chat.chat_id
        elif isinstance(self._peer_chat, InputPeerChannel):
            self._chat_id = -1000000000000 - self._peer_chat.channel_id

        if self._client.listening.get(self._chat_id, False):
            raise AlreadyInConversationError()
        self._cancelled = False
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.cancel()
