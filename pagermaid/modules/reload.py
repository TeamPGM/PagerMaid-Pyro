import asyncio

from pyrogram.raw.functions import PingDelayDisconnect

from pagermaid import read_context, logs
from pagermaid.common.reload import reload_all
from pagermaid.enums import Message
from pagermaid.listener import listener
from pagermaid.services import bot, scheduler
from pagermaid.utils import lang

ping_watchdog_event = asyncio.Event()


@listener(
    is_plugin=False, command="reload", need_admin=True, description=lang("reload_des")
)
async def reload_plugins(message: Message):
    """To reload plugins."""
    await reload_all()
    await message.edit(lang("reload_ok"))


@scheduler.scheduled_job("cron", hour="4", id="reload.clear_read_context")
async def clear_read_context_cron():
    read_context.clear()


@scheduler.scheduled_job("interval", seconds=10, id="reload.ping_watchdog")
async def ping_task():
    if not bot.is_initialized:
        return
    if ping_watchdog_event.is_set():
        logs.debug("Ping task watchdog event set, skip")
        return
    logs.debug("Ping task running")
    try:
        await bot.session.invoke(
            PingDelayDisconnect(
                ping_id=0,
                disconnect_delay=bot.session.WAIT_TIMEOUT + 10,
            ),
            retries=0,
        )
    except OSError:
        logs.debug("Ping task raise OSError, try restart")
        ping_watchdog_event.set()
        try:
            await bot.restart()
        finally:
            ping_watchdog_event.clear()
    logs.debug("Ping task ok")
