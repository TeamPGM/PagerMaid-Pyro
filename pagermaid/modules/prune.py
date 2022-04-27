""" Module to automate message deletion. """

from asyncio import sleep

from pyrogram import Client

from pagermaid import log
from pagermaid.listener import listener
from pagermaid.utils import lang, Message


@listener(is_plugin=False, outgoing=True, command="prune",
          need_admin=True,
          description=lang('prune_des'))
async def prune(client: Client, message: Message):
    """ Purge every single message after the message you replied to. """
    if not message.reply_to_message:
        await message.edit(lang('not_reply'))
        return
    input_chat = message.chat.id
    messages = []
    count = 0
    async for msg in client.get_chat_history(input_chat,
                                             limit=message.id - message.reply_to_message.id + 1):
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


@listener(is_plugin=False, outgoing=True, command="selfprune",
          need_admin=True,
          description=lang('sp_des'),
          parameters=lang('sp_parameters'))
async def self_prune(client: Client, message: Message):
    """ Deletes specific amount of messages you sent. """
    msgs = []
    count_buffer = 0
    if not len(message.parameter) == 1:
        if not message.reply_to_message:
            return await message.edit(lang('arg_error'))
        async for msg in client.search_messages(
                message.chat.id,
                from_user="me",
                offset=message.reply_to_message.id,
        ):
            msgs.append(msg.id)
            count_buffer += 1
            if len(msgs) == 100:
                await client.delete_messages(message.chat.id, msgs)
                msgs = []
        if msgs:
            await client.delete_messages(message.chat.id, msgs)
        if count_buffer == 0:
            await message.delete()
            count_buffer += 1
        await log(f"{lang('prune_hint1')}{lang('sp_hint')} {str(count_buffer)} {lang('prune_hint2')}")
        notification = await send_prune_notify(client, message, count_buffer, count_buffer)
        await sleep(1)
        await notification.delete()
        return
    try:
        count = int(message.parameter[0])
        await message.delete()
    except ValueError:
        await message.edit(lang('arg_error'))
        return
    async for msg in client.search_messages(message.chat.id, from_user="me"):
        if count_buffer == count:
            break
        msgs.append(msg.id)
        count_buffer += 1
        if len(msgs) == 100:
            await client.delete_messages(message.chat.id, msgs)
            msgs = []
    if msgs:
        await client.delete_messages(message.chat.id, msgs)
    await log(f"{lang('prune_hint1')}{lang('sp_hint')} {str(count_buffer)} / {str(count)} {lang('prune_hint2')}")
    try:
        notification = await send_prune_notify(client, message, count_buffer, count)
        await sleep(1)
        await notification.delete()
    except ValueError:
        pass


@listener(is_plugin=False, outgoing=True, command="yourprune",
          need_admin=True,
          description=lang('yp_des'),
          parameters=lang('sp_parameters'))
async def your_prune(client: Client, message: Message):
    """ Deletes specific amount of messages someone sent. """
    if not message.reply_to_message:
        return await message.edit(lang('not_reply'))
    target = message.reply_to_message
    if not target.from_user:
        return await message.edit(lang('not_reply'))
    if not len(message.parameter) == 1:
        return await message.edit(lang('arg_error'))
    count = 0
    try:
        count = int(message.parameter[0])
        await message.delete()
    except ValueError:
        return await message.edit(lang('arg_error'))
    except Exception:  # noqa
        pass
    count_buffer = 0
    async for msg in client.search_messages(message.chat.id, from_user=target.from_user.id):
        if count_buffer == count:
            break
        await msg.delete()
        count_buffer += 1
    await log(f"{lang('prune_hint1')}{lang('yp_hint')} {str(count_buffer)} / {str(count)} {lang('prune_hint2')}")
    notification = await send_prune_notify(client, message, count_buffer, count)
    await sleep(1)
    await notification.delete()


@listener(is_plugin=False, outgoing=True, command="del",
          need_admin=True,
          description=lang('del_des'))
async def delete(_: Client, message: Message):
    """ Deletes the message you replied to. """
    target = message.reply_to_message
    if target:
        try:
            await target.delete()
        except Exception as e:  # noqa
            pass
        await message.delete()
        await log(lang('del_notification'))
    else:
        await message.delete()


async def send_prune_notify(client, message, count_buffer, count):
    return await client.send_message(
        message.chat.id,
        "%s %s / %s %s" % (lang('spn_deleted'), str(count_buffer), str(count), lang('prune_hint2'))
    )
