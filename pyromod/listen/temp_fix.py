import pyrogram


async def temp_fix(
    client: "pyrogram.Client",
    message: pyrogram.raw.base.Message,
    users: dict,
    chats: dict,
    is_scheduled: bool = False,
    replies: int = 1
):
    parsed = await pyrogram.types.Message.old_parse(client, message, users, chats, is_scheduled, replies)  # noqa
    if isinstance(message, pyrogram.raw.types.Message) and message.reply_to \
            and message.reply_to.forum_topic and not message.reply_to.reply_to_top_id:
        parsed.reply_to_top_message_id = parsed.reply_to_message_id
        parsed.reply_to_message_id = None
        parsed.reply_to_message = None
    return parsed
