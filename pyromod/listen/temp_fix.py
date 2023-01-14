import contextlib
from typing import Union

import pyrogram
from pyrogram.errors import BadRequest


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
            and hasattr(message.reply_to, "forum_topic") and message.reply_to.forum_topic \
            and not message.reply_to.reply_to_top_id:
        parsed.reply_to_top_message_id = parsed.reply_to_message_id
        parsed.reply_to_message_id = None
        parsed.reply_to_message = None
    # make message.text as message.caption
    parsed.text = parsed.text or parsed.caption
    return parsed


async def read_chat_history(
    self: "pyrogram.Client",
    chat_id: Union[int, str],
    max_id: int = 0
) -> bool:

    peer = await self.resolve_peer(chat_id)

    if isinstance(peer, pyrogram.raw.types.InputPeerChannel):
        q = pyrogram.raw.functions.channels.ReadHistory(
            channel=peer,
            max_id=max_id
        )
    else:
        q = pyrogram.raw.functions.messages.ReadHistory(
            peer=peer,
            max_id=max_id
        )

    await self.invoke(q)

    if isinstance(peer, pyrogram.raw.types.InputPeerChannel):
        with contextlib.suppress(BadRequest):
            topics: pyrogram.raw.types.messages.ForumTopics = await self.invoke(
                pyrogram.raw.functions.channels.GetForumTopics(
                    channel=peer,
                    offset_date=0,
                    offset_id=0,
                    offset_topic=0,
                    limit=0
                )
            )
            for i in topics.topics:
                await self.invoke(
                    pyrogram.raw.functions.messages.ReadDiscussion(
                        peer=peer,
                        msg_id=i.id,
                        read_max_id=i.read_inbox_max_id + i.unread_count,
                    )
                )

    return True
