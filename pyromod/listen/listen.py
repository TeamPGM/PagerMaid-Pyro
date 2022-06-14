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
import functools
from typing import Optional, List

import pyrogram

from pagermaid.single_utils import get_sudo_list, Message

from ..utils import patch, patchable


class ListenerCanceled(Exception):
    pass


pyrogram.errors.ListenerCanceled = ListenerCanceled


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
        future.add_done_callback(
            functools.partial(self.clear_listener, chat_id)
        )
        self.listening.update({
            chat_id: {"future": future, "filters": filters}
        })
        return await asyncio.wait_for(future, timeout, loop=self.loop)

    @patchable
    async def ask(self, chat_id, text, filters=None, timeout=None, *args, **kwargs):
        request = await self.send_message(chat_id, text, *args, **kwargs)
        response = await self.listen(chat_id, filters, timeout)
        response.request = request
        return response

    @patchable
    def clear_listener(self, chat_id, future):
        if future == self.listening[chat_id]["future"]:
            self.listening.pop(chat_id, None)

    @patchable
    def cancel_listener(self, chat_id):
        listener = self.listening.get(chat_id)
        if not listener or listener['future'].done():
            return

        listener['future'].set_exception(ListenerCanceled())
        self.clear_listener(chat_id, listener['future'])


@patch(pyrogram.handlers.message_handler.MessageHandler)
class MessageHandler:
    @patchable
    def __init__(self, callback: callable, filters=None):
        self.user_callback = callback
        self.old__init__(self.resolve_listener, filters)

    @patchable
    async def resolve_listener(self, client, message, *args):
        listener = client.listening.get(message.chat.id)
        if listener and not listener['future'].done():
            listener['future'].set_result(message)
        else:
            if listener and listener['future'].done():
                client.clear_listener(message.chat.id, listener['future'])
            await self.user_callback(client, message, *args)

    @patchable
    async def check(self, client, update):
        listener = client.listening.get(update.chat.id)

        if listener and not listener['future'].done():
            return await listener['filters'](client, update) if callable(listener['filters']) else True

        return (
            await self.filters(client, update)
            if callable(self.filters)
            else True
        )


@patch(pyrogram.types.user_and_chats.chat.Chat)
class Chat(pyrogram.types.Chat):
    @patchable
    def listen(self, *args, **kwargs):
        return self._client.listen(self.id, *args, **kwargs)

    @patchable
    def ask(self, *args, **kwargs):
        return self._client.ask(self.id, *args, **kwargs)

    @patchable
    def cancel_listener(self):
        return self._client.cancel_listener(self.id)


@patch(pyrogram.types.user_and_chats.user.User)
class User(pyrogram.types.User):
    @patchable
    def listen(self, *args, **kwargs):
        return self._client.listen(self.id, *args, **kwargs)

    @patchable
    def ask(self, *args, **kwargs):
        return self._client.ask(self.id, *args, **kwargs)

    @patchable
    def cancel_listener(self):
        return self._client.cancel_listener(self.id)

# pagermaid-pyro


@patch(pyrogram.types.messages_and_media.Message)
class Message(pyrogram.types.Message):
    @patchable
    async def safe_delete(self, revoke: bool = True):
        try:
            return await self._client.delete_messages(
                chat_id=self.chat.id,
                message_ids=self.id,
                revoke=revoke
            )
        except Exception as e:  # noqa
            return False

    @patchable
    def obtain_message(self) -> Optional[str]:
        """ Obtains a message from either the reply message or command arguments. """
        return self.arguments or (
            self.reply_to_message.text if self.reply_to_message else None
        )

    @patchable
    def obtain_user(self) -> Optional[int]:
        """ Obtains a user from either the reply message or command arguments. """
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
                if self.entities[0].type == pyrogram.enums.MessageEntityType.TEXT_MENTION:
                    user = self.entities[0].user.id
        if not user and self.chat.type == pyrogram.enums.ChatType.PRIVATE:  # Current chat
            user = self.chat.id
        return user

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
        from_id = self.from_user.id if self.from_user else self.sender_chat.id
        is_self = self.from_user.is_self if self.from_user else False

        if len(text) < 4096:
            if from_id in sudo_users or self.chat.id in sudo_users:
                if reply_to and (not is_self) and (not no_reply):
                    msg = await reply_to.reply(
                        text=text,
                        parse_mode=parse_mode,
                        disable_web_page_preview=disable_web_page_preview
                    )
                elif is_self:
                    msg = await self._client.edit_message_text(
                        chat_id=self.chat.id,
                        message_id=self.id,
                        text=text,
                        parse_mode=parse_mode,
                        entities=entities,
                        disable_web_page_preview=disable_web_page_preview,
                        reply_markup=reply_markup
                    )
                elif not no_reply:
                    msg = await self.reply(
                        text=text,
                        parse_mode=parse_mode,
                        disable_web_page_preview=disable_web_page_preview
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
                        reply_markup=reply_markup
                    )
                except pyrogram.errors.exceptions.forbidden_403.MessageAuthorRequired:  # noqa
                    if not no_reply:
                        msg = await self.reply(
                            text=text,
                            parse_mode=parse_mode,
                            entities=entities,
                            disable_web_page_preview=disable_web_page_preview,
                            reply_markup=reply_markup
                        )
        else:
            with open("output.log", "w+") as file:
                file.write(text)
            msg = await self._client.send_document(
                chat_id=self.chat.id,
                document="output.log",
                reply_to_message_id=self.id
            )
        if not msg:
            return self
        msg.parameter = self.parameter
        msg.arguments = self.arguments
        return msg

    edit = edit_text
