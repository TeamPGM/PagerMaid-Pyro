""" Module to automate message deletion. """

import contextlib
from asyncio import sleep

from pagermaid.enums import Client, Message
from pagermaid.listener import listener
from pagermaid.utils import lang
from pagermaid.utils.bot_utils import log


@listener(
    is_plugin=False,
    outgoing=True,
    command="prune",
    need_admin=True,
    description=lang("prune_des"),
)
async def prune(client: Client, message: Message):
    """Purge every single message after the message you replied to."""
    if not message.reply_to_message:
        await message.edit(lang("not_reply"))
        return
    input_chat = message.chat.id
    messages = []
    count = 0
    limit = message.id - message.reply_to_message.id + 1
    if message.message_thread_id:
        func = client.get_discussion_replies(
            input_chat, message.message_thread_id, limit=limit
        )
    else:
        func = client.get_chat_history(input_chat, limit=limit)
    async for msg in func:
        if msg.id < message.reply_to_message.id:
            break
        messages.append(msg.id)
        count += 1
        if msg.reply_to_message:
            messages.append(msg.reply_to_message.id)
        if len(messages) == 100:
            await client.delete_messages(input_chat, messages)
            messages = []

    if messages:
        await client.delete_messages(input_chat, messages)
    await log(f"{lang('prune_hint1')} {str(count)} {lang('prune_hint2')}")
    notification = await send_prune_notify(client, message, count, count)
    await sleep(1)
    await notification.delete()


@listener(
    is_plugin=False,
    outgoing=True,
    command="selfprune",
    need_admin=True,
    description=lang("sp_des"),
    parameters=lang("sp_parameters"),
)
async def self_prune(bot: Client, message: Message):
    """Deletes specific amount of messages you sent."""
    msgs = []
    count_buffer = 0
    offset = 0
    if len(message.parameter) != 1:
        if not message.reply_to_message:
            return await message.edit(lang("arg_error"))
        offset = message.reply_to_message.id
    try:
        count = int(message.parameter[0])
        await message.delete()
    except ValueError:
        await message.edit(lang("arg_error"))
        return
    async for msg in bot.get_chat_history(message.chat.id, limit=100):
        if count_buffer == count:
            break
        if msg.from_user and msg.from_user.is_self:
            msgs.append(msg.id)
            count_buffer += 1
            if len(msgs) == 100:
                await bot.delete_messages(message.chat.id, msgs)
                msgs = []
    async for msg in bot.search_messages(
        message.chat.id, from_user="me", offset=offset
    ):
        if count_buffer == count:
            break
        msgs.append(msg.id)
        count_buffer += 1
        if len(msgs) == 100:
            await bot.delete_messages(message.chat.id, msgs)
            msgs = []
    if msgs:
        await bot.delete_messages(message.chat.id, msgs)
    await log(
        f"{lang('prune_hint1')}{lang('sp_hint')} {str(count_buffer)} / {count} {lang('prune_hint2')}"
    )

    with contextlib.suppress(ValueError):
        notification = await send_prune_notify(bot, message, count_buffer, count)
        await sleep(1)
        await notification.delete()


@listener(
    is_plugin=False,
    outgoing=True,
    command="yourprune",
    need_admin=True,
    description=lang("yp_des"),
    parameters=lang("sp_parameters"),
)
async def your_prune(bot: Client, message: Message):
    """Deletes specific amount of messages someone sent."""
    if not message.reply_to_message:
        return await message.edit(lang("not_reply"))
    target = message.reply_to_message
    if not target.from_user:
        return await message.edit(lang("not_reply"))
    if len(message.parameter) != 1:
        return await message.edit(lang("arg_error"))
    count = 0
    try:
        count = int(message.parameter[0])
        await message.delete()
    except ValueError:
        return await message.edit(lang("arg_error"))
    except Exception:  # noqa
        pass
    count_buffer = 0
    msgs = []
    async for msg in bot.get_chat_history(message.chat.id, limit=100):
        if count_buffer == count:
            break
        if msg.from_user and msg.from_user.id == target.from_user.id:
            msgs.append(msg.id)
            count_buffer += 1
            if len(msgs) == 100:
                await bot.delete_messages(message.chat.id, msgs)
                msgs = []
    async for msg in bot.search_messages(
        message.chat.id, from_user=target.from_user.id
    ):
        if count_buffer == count:
            break
        count_buffer += 1
        msgs.append(msg.id)
        if len(msgs) == 100:
            await bot.delete_messages(message.chat.id, msgs)
            msgs = []
    if msgs:
        await bot.delete_messages(message.chat.id, msgs)
    await log(
        f"{lang('prune_hint1')}{lang('yp_hint')} {str(count_buffer)} / {count} {lang('prune_hint2')}"
    )

    with contextlib.suppress(ValueError):
        notification = await send_prune_notify(bot, message, count_buffer, count)
        await sleep(1)
        await notification.delete()


@listener(
    is_plugin=False,
    outgoing=True,
    command="del",
    need_admin=True,
    description=lang("del_des"),
)
async def delete(message: Message):
    """Deletes the message you replied to."""
    if target := message.reply_to_message:
        with contextlib.suppress(Exception):
            await target.delete()
        await message.delete()
        await log(lang("del_notification"))
    else:
        await message.delete()


async def send_prune_notify(bot: Client, message: Message, count_buffer, count):
    return await bot.send_message(
        message.chat.id,
        f"{lang('spn_deleted')} {str(count_buffer)} / {str(count)} {lang('prune_hint2')}",
        message_thread_id=message.message_thread_id,
    )
