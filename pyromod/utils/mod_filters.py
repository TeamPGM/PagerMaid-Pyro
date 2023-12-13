from pyrogram.filters import create

from pagermaid.enums import Message


async def reacted_filter(_, __, m: Message):
    return m.reactions is not None


reacted = create(reacted_filter)
"""Filter messages that are reacted."""
