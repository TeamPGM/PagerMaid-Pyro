""" Pagermaid message plugin. """
from pyrogram.enums import ChatType
from pyrogram.errors import Forbidden, FloodWait
from pyrogram.raw.functions.messages import ForwardMessages

from pagermaid import log
from pagermaid.config import Config
from pagermaid.listener import listener
from pagermaid.utils import lang
from pagermaid.enums import Client, Message


@listener(is_plugin=False, outgoing=True, command="id", description=lang("id_des"))
async def userid(message: Message):
    """Query the UserID of the sender of the message you replied to."""
    reply = message.reply_to_message
    text = f"Message ID: `{str(message.id)}" + "`\n\n"
    text += "**Chat**\nid:`" + str(message.chat.id) + "`\n"
    msg_from = message.chat
    if msg_from.type == ChatType.PRIVATE:
        try:
            text += f"first_name: `{msg_from.first_name}" + "`\n"
        except TypeError:
            text += "**死号**\n"
        if msg_from.last_name:
            text += f"last_name: `{msg_from.last_name}" + "`\n"
        if msg_from.username:
            text += f"username: @{msg_from.username}" + "\n"
    if msg_from.type in [ChatType.SUPERGROUP, ChatType.CHANNEL]:
        text += f"title: `{msg_from.title}" + "`\n"
        try:
            if msg_from.username:
                text += f"username: @{msg_from.username}" + "\n"
        except AttributeError:
            return await message.edit(lang("leave_not_group"))
        text += f"protected: `{str(msg_from.has_protected_content)}" + "`\n"
    if reply:
        text += "\n" + lang("id_hint") + "\nMessage ID: `" + str(reply.id) + "`"
        try:
            text += "\n\n**User**\nid: `" + str(reply.from_user.id) + "`"
            if reply.from_user.is_bot:
                text += f"\nis_bot: {lang('id_is_bot_yes')}"
            try:
                text += "\nfirst_name: `" + reply.from_user.first_name + "`"
            except TypeError:
                text += f"\n**{lang('id_da')}**"
            if reply.from_user.last_name:
                text += "\nlast_name: `" + reply.from_user.last_name + "`"
            if reply.from_user.username:
                text += "\nusername: @" + reply.from_user.username
            if reply.from_user.dc_id:
                text += "\ndc: `" + str(reply.from_user.dc_id) + "`"
        except AttributeError:
            pass
        try:
            text += "\n\n**Chat**\nid: `" + str(reply.sender_chat.id) + "`"
            text += "\ntitle: `" + reply.sender_chat.title + "`"
            if reply.sender_chat.username:
                text += "\nusername: @" + reply.sender_chat.username
        except AttributeError:
            pass
        if reply.forward_from_chat:
            text += (
                "\n\n**Forward From Channel**\n"
                "id: `"
                + str(reply.forward_from_chat.id)
                + "`\ntitle: `"
                + reply.forward_from_chat.title
                + "`"
            )
            if reply.forward_from_chat.username:
                text += "\nusername: @" + reply.forward_from_chat.username
            if reply.forward_from_message_id:
                text += "\nmessage_id: `" + str(reply.forward_from_message_id) + "`"
            if reply.forward_sender_name:
                text += "\npost_author: `" + reply.forward_sender_name + "`"
        elif reply.forward_from:
            text += (
                "\n\n**Forward From User**\nid: `" + str(reply.forward_from.id) + "`"
            )
            try:
                if reply.forward_from.is_bot:
                    text += f"\nis_bot: {lang('id_is_bot_yes')}"
                try:
                    text += "\nfirst_name: `" + reply.forward_from.first_name + "`"
                except TypeError:
                    text += f"\n**{lang('id_da')}**"
                if reply.forward_from.last_name:
                    text += "\nlast_name: `" + reply.forward_from.last_name + "`"
                if reply.forward_from.username:
                    text += "\nusername: @" + reply.forward_from.username
                if reply.forward_from.dc_id:
                    text += "\ndc: `" + str(reply.forward_from.dc_id) + "`"
            except AttributeError:
                pass
        elif reply.forward_sender_name:
            text += (
                "\n\n**Forward From User**\nsender_name: `"
                + str(reply.forward_sender_name)
                + "`"
            )
    await message.edit(text)


@listener(
    is_plugin=False,
    outgoing=True,
    command="uslog",
    description=lang("uslog_des"),
    parameters="<string>",
)
async def uslog(message: Message):
    """Forwards a message into log group"""
    if Config.LOG:
        if message.reply_to_message:
            reply_msg = message.reply_to_message
            await reply_msg.forward(Config.LOG_ID)
        elif message.arguments:
            await log(message.arguments)
        else:
            return await message.edit(lang("arg_error"))
        await message.edit(lang("uslog_success"))
    else:
        await message.edit(lang("uslog_log_disable"))


@listener(
    is_plugin=False,
    outgoing=True,
    command="log",
    description=lang("log_des"),
    parameters="<string>",
)
async def logging(message: Message):
    """Forwards a message into log group"""
    if Config.LOG:
        if message.reply_to_message:
            reply_msg = message.reply_to_message
            await reply_msg.forward(Config.LOG_ID)
        elif message.arguments:
            await log(message.arguments)
        else:
            return await message.edit(lang("arg_error"))
        await message.safe_delete()
    else:
        await message.edit(lang("uslog_log_disable"))


@listener(
    is_plugin=False,
    outgoing=True,
    command="re",
    description=lang("re_des"),
    parameters=lang("re_parameters"),
)
async def re(bot: Client, message: Message):
    """Forwards a message into this group"""
    if reply := message.reply_to_message:
        if message.arguments == "":
            num = 1
        else:
            try:
                num = int(message.arguments)
                if num > 100:
                    await message.edit(lang("re_too_big"))
            except Exception:
                return await message.edit(lang("re_arg_error"))
        await message.safe_delete()
        for _ in range(num):
            try:
                if not message.chat.has_protected_content:
                    await forward_msg(bot, message.reply_to_message)
                else:
                    await reply.copy(
                        reply.chat.id,
                        reply_to_message_id=message.reply_to_top_message_id,
                    )
            except (Forbidden, FloodWait, Exception):
                return
    else:
        await message.edit(lang("not_reply"))


async def forward_msg(bot: Client, message: Message):
    message_ids = [message.id]
    await bot.invoke(
        ForwardMessages(
            to_peer=await bot.resolve_peer(message.chat.id),
            from_peer=await bot.resolve_peer(message.chat.id),
            id=message_ids,
            silent=None,
            random_id=[bot.rnd_id() for _ in message_ids],
            schedule_date=None,
            noforwards=None,
            top_msg_id=message.reply_to_top_message_id,
        )
    )
