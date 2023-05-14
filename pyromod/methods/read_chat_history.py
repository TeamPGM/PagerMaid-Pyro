import contextlib
from typing import Union

import pyrogram


async def read_chat_history(
        self: "pyrogram.Client", chat_id: Union[int, str], max_id: int = 0
) -> bool:
    peer = await self.resolve_peer(chat_id)
    if isinstance(peer, pyrogram.raw.types.InputPeerChannel):
        with contextlib.suppress(pyrogram.errors.BadRequest):  # noqa
            topics: pyrogram.raw.types.messages.ForumTopics = await self.invoke(
                pyrogram.raw.functions.channels.GetForumTopics(
                    channel=peer,  # noqa
                    offset_date=0,
                    offset_id=0,
                    offset_topic=0,
                    limit=0,
                )
            )
            for i in topics.topics:
                if isinstance(i, pyrogram.raw.types.ForumTopic):
                    await self.invoke(
                        pyrogram.raw.functions.messages.ReadDiscussion(
                            peer=peer,
                            msg_id=i.id,
                            read_max_id=i.top_message,
                        )
                    )
    return await self.oldread_chat_history(chat_id, max_id)  # noqa
