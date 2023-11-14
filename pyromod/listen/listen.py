"""
pyromod - A monkeypatcher add-on for Pyrogram
Copyright (C) 2020 Cezar H. <https://github.com/usernein>

This file is part of pyromod.

pyromod is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

pyromod is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with pyromod.  If not, see <https://www.gnu.org/licenses/>.
"""

import asyncio
import contextlib
import functools
from datetime import datetime
from typing import Optional, List, Union

import pyrogram
from pyrogram.enums import ChatType

from pagermaid.single_utils import get_sudo_list
from pagermaid.scheduler import add_delete_message_job
from ..methods.get_dialogs_list import get_dialogs_list as get_dialogs_list_func
from ..methods.read_chat_history import read_chat_history as read_chat_history_func

from ..utils import patch, patchable
from ..utils.conversation import Conversation
from ..utils.errors import TimeoutConversationError, ListenerCanceled

pyrogram.errors.ListenerCanceled = ListenerCanceled  # noqa


@patch(pyrogram.client.Client)
class Client:
    @patchable
    def __init__(self, *args, **kwargs):
        self.listening = {}
        self.using_mod = True

        self.old__init__(*args, **kwargs)

    @patchable
    async def listen(self, chat_id, filters=None, timeout=None):
        if type(chat_id) != int:
            chat = await self.get_chat(chat_id)
            chat_id = chat.id

        future = self.loop.create_future()
        future.add_done_callback(functools.partial(self.clear_listener, chat_id))
        self.listening.update({chat_id: {"future": future, "filters": filters}})
        try:
            return await asyncio.wait_for(future, timeout)
        except asyncio.exceptions.TimeoutError as e:
            raise TimeoutConversationError() from e

    @patchable
    async def ask(self, chat_id, text, filters=None, timeout=None, *args, **kwargs):
        request = await self.send_message(chat_id, text, *args, **kwargs)
        response = await self.listen(chat_id, filters, timeout)
        response.request = request
        return response

    @patchable
    def clear_listener(self, chat_id, future):
        with contextlib.suppress(KeyError):
            if future == self.listening[chat_id]["future"]:
                self.listening.pop(chat_id, None)

    @patchable
    def cancel_listener(self, chat_id):
        listener = self.listening.get(chat_id)
        if not listener or listener["future"].done():
            return

        listener["future"].set_exception(ListenerCanceled())
        self.clear_listener(chat_id, listener["future"])

    @patchable
    def cancel_all_listener(self):
        for chat_id in self.listening:
            self.cancel_listener(chat_id)

    @patchable
    def conversation(
        self, chat_id: Union[int, str], once_timeout: int = 60, filters=None
    ):
        return Conversation(self, chat_id, once_timeout, filters)

    @patchable
    async def read_chat_history(
        self: "pyrogram.Client", chat_id: Union[int, str], max_id: int = 0
    ) -> bool:
        return await read_chat_history_func(self, chat_id, max_id)

    @patchable
    async def get_dialogs_list(self: "Client"):
        return await get_dialogs_list_func(self)


@patch(pyrogram.handlers.message_handler.MessageHandler)
class MessageHandler:
    @patchable
    def __init__(self, callback: callable, filters=None):
        self.user_callback = callback
        self.old__init__(self.resolve_listener, filters)

    @patchable
    async def resolve_listener(self, client, message, *args):
        listener = client.listening.get(message.chat.id)
        if listener and not listener["future"].done():
            listener["future"].set_result(message)
        else:
            if listener and listener["future"].done():
                client.clear_listener(message.chat.id, listener["future"])
            await self.user_callback(client, message, *args)

    @patchable
    async def check(self, client, update):
        listener = client.listening.get(update.chat.id)

        if listener and not listener["future"].done():
            return (
                await listener["filters"](client, update)
                if callable(listener["filters"])
                else True
            )

        return await self.filters(client, update) if callable(self.filters) else True


@patch(pyrogram.handlers.edited_message_handler.EditedMessageHandler)
class EditedMessageHandler:
    @patchable
    def __init__(self, callback: callable, filters=None):
        self.user_callback = callback
        self.old__init__(self.resolve_listener, filters)

    @patchable
    async def resolve_listener(self, client, message, *args):
        listener = client.listening.get(message.chat.id)
        if listener and not listener["future"].done():
            listener["future"].set_result(message)
        else:
            if listener and listener["future"].done():
                client.clear_listener(message.chat.id, listener["future"])
            await self.user_callback(client, message, *args)

    @patchable
    async def check(self, client, update):
        listener = client.listening.get(update.chat.id)

        if listener and not listener["future"].done():
            return (
                await listener["filters"](client, update)
                if callable(listener["filters"])
                else True
            )

        return await self.filters(client, update) if callable(self.filters) else True


@patch(pyrogram.types.user_and_chats.chat.Chat)
class Chat(pyrogram.types.Chat):
    @patchable
    def listen(self, *args, **kwargs):
        return self._client.listen(self.id, *args, **kwargs)  # noqa

    @patchable
    def ask(self, *args, **kwargs):
        return self._client.ask(self.id, *args, **kwargs)  # noqa

    @patchable
    def cancel_listener(self):
        return self._client.cancel_listener(self.id)  # noqa

    @patchable
    @staticmethod
    def _parse_user_chat(client, user: pyrogram.raw.types.User) -> "Chat":
        chat = pyrogram.types.user_and_chats.chat.Chat.old_parse_user_chat(
            client, user
        )  # noqa
        chat.is_forum = None
        return chat

    @patchable
    @staticmethod
    def _parse_chat_chat(client, chat: pyrogram.raw.types.Chat) -> "Chat":
        chat = pyrogram.types.user_and_chats.chat.Chat.old_parse_chat_chat(
            client, chat
        )  # noqa
        chat.is_forum = None
        return chat

    @patchable
    @staticmethod
    def _parse_channel_chat(client, channel: pyrogram.raw.types.Channel) -> "Chat":
        chat = pyrogram.types.user_and_chats.chat.Chat.old_parse_channel_chat(
            client, channel
        )  # noqa
        chat.is_forum = getattr(channel, "forum", None)
        return chat


@patch(pyrogram.types.user_and_chats.user.User)
class User(pyrogram.types.User):
    @patchable
    def listen(self, *args, **kwargs):
        return self._client.listen(self.id, *args, **kwargs)  # noqa

    @patchable
    def ask(self, *args, **kwargs):
        return self._client.ask(self.id, *args, **kwargs)  # noqa

    @patchable
    def cancel_listener(self):
        return self._client.cancel_listener(self.id)  # noqa


# pagermaid-pyro


@patch(pyrogram.types.messages_and_media.Message)
class Message(pyrogram.types.Message):
    @patchable
    async def safe_delete(self, revoke: bool = True):
        try:
            return await self._client.delete_messages(
                chat_id=self.chat.id, message_ids=self.id, revoke=revoke
            )
        except Exception:  # noqa
            return False

    @patchable
    def obtain_message(self) -> Optional[str]:
        """Obtains a message from either the reply message or command arguments."""
        return self.arguments or (
            self.reply_to_message.text if self.reply_to_message else None
        )

    @patchable
    def obtain_user(self) -> Optional[int]:
        """Obtains a user from either the reply message or command arguments."""
        user = None
        # Priority: reply > argument > current_chat
        if self.reply_to_message:  # Reply to a user
            user = self.reply_to_message.from_user
            if user:
                user = user.id
        if not user and len(self.parameter) == 1:  # Argument provided
            (raw_user,) = self.parameter
            if raw_user.isnumeric():
                user = int(raw_user)
            elif self.entities is not None:
                if (
                    self.entities[0].type
                    == pyrogram.enums.MessageEntityType.TEXT_MENTION
                ):
                    user = self.entities[0].user.id
        if (
            not user and self.chat.type == pyrogram.enums.ChatType.PRIVATE
        ):  # Current chat
            user = self.chat.id
        return user

    @patchable
    async def delay_delete(self, delay: int = 60):
        add_delete_message_job(self, delay)

    @patchable
    async def edit_text(
        self,
        text: str,
        parse_mode: Optional["pyrogram.enums.ParseMode"] = None,
        entities: List["pyrogram.types.MessageEntity"] = None,
        disable_web_page_preview: bool = None,
        reply_markup: "pyrogram.types.InlineKeyboardMarkup" = None,
        no_reply: bool = None,
    ) -> "Message":
        msg = None
        sudo_users = get_sudo_list()
        reply_to = self.reply_to_message
        from_id = self.chat.id
        is_self = False
        if self.from_user or self.sender_chat:
            from_id = self.from_user.id if self.from_user else self.sender_chat.id
        elif self.chat.type == ChatType.PRIVATE:
            is_self = True
        is_self = self.from_user.is_self if self.from_user else is_self

        if len(text) < 4096:
            if from_id in sudo_users or self.chat.id in sudo_users:
                if reply_to and (not is_self) and (not no_reply):
                    msg = await reply_to.reply(
                        text=text,
                        parse_mode=parse_mode,
                        disable_web_page_preview=disable_web_page_preview,
                        quote=True,
                    )
                elif is_self:
                    msg = await self._client.edit_message_text(
                        chat_id=self.chat.id,
                        message_id=self.id,
                        text=text,
                        parse_mode=parse_mode,
                        entities=entities,
                        disable_web_page_preview=disable_web_page_preview,
                        reply_markup=reply_markup,
                    )
                elif not no_reply:
                    msg = await self.reply(
                        text=text,
                        parse_mode=parse_mode,
                        disable_web_page_preview=disable_web_page_preview,
                        quote=True,
                    )
            else:
                try:
                    msg = await self._client.edit_message_text(
                        chat_id=self.chat.id,
                        message_id=self.id,
                        text=text,
                        parse_mode=parse_mode,
                        entities=entities,
                        disable_web_page_preview=disable_web_page_preview,
                        reply_markup=reply_markup,
                    )
                except (
                    pyrogram.errors.exceptions.forbidden_403.MessageAuthorRequired
                ):  # noqa
                    if not no_reply:
                        msg = await self.reply(
                            text=text,
                            parse_mode=parse_mode,
                            entities=entities,
                            disable_web_page_preview=disable_web_page_preview,
                            reply_markup=reply_markup,
                            quote=True,
                        )
        else:
            with open("output.log", "w+") as file:
                file.write(text)
            msg = await self._client.send_document(
                chat_id=self.chat.id, document="output.log", reply_to_message_id=self.id
            )
        if not msg:
            return self
        msg.parameter = self.parameter if hasattr(self, "parameter") else []
        msg.arguments = self.arguments if hasattr(self, "arguments") else ""
        return msg

    edit = edit_text

    @patchable
    @staticmethod
    async def _parse(
        client: "pyrogram.Client",
        message: pyrogram.raw.base.Message,
        users: dict,
        chats: dict,
        is_scheduled: bool = False,
        replies: int = 1,
    ):
        parsed = await pyrogram.types.Message.old_parse(
            client, message, users, chats, is_scheduled, replies
        )  # noqa
        # forum topic
        if isinstance(message, pyrogram.raw.types.Message):
            parsed.forum_topic = getattr(message.reply_to, "forum_topic", None)
            if (
                message.reply_to
                and parsed.forum_topic
                and not message.reply_to.reply_to_top_id
            ):
                parsed.reply_to_top_message_id = parsed.reply_to_message_id
                parsed.reply_to_message_id = None
                parsed.reply_to_message = None
        # make message.text as message.caption
        parsed.text = parsed.text or parsed.caption
        return parsed

    @patchable
    async def copy(
        self,
        chat_id: Union[int, str],
        caption: str = None,
        parse_mode: Optional["pyrogram.enums.ParseMode"] = None,
        caption_entities: List["pyrogram.types.MessageEntity"] = None,
        disable_notification: bool = None,
        reply_to_message_id: int = None,
        schedule_date: datetime = None,
        protect_content: bool = None,
        reply_markup: Union[
            "pyrogram.types.InlineKeyboardMarkup",
            "pyrogram.types.ReplyKeyboardMarkup",
            "pyrogram.types.ReplyKeyboardRemove",
            "pyrogram.types.ForceReply",
        ] = object,
        **kwargs
    ) -> Union["pyrogram.types.Message", List["pyrogram.types.Message"]]:
        if self.media:
            self.text = None
        return await self.oldcopy(
            chat_id=chat_id,
            caption=caption,
            parse_mode=parse_mode,
            caption_entities=caption_entities,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            schedule_date=schedule_date,
            protect_content=protect_content,
            reply_markup=reply_markup,
            **kwargs
        )  # noqa


@patch(pyrogram.dispatcher.Dispatcher)  # noqa
class Dispatcher(pyrogram.dispatcher.Dispatcher):  # noqa
    @patchable
    def remove_all_handlers(self):
        async def fn():
            for lock in self.locks_list:
                await lock.acquire()

            self.groups.clear()

            for lock in self.locks_list:
                lock.release()

        self.loop.create_task(fn())
