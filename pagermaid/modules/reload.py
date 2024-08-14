from pagermaid import read_context
from pagermaid.common.reload import reload_all
from pagermaid.enums import Message
from pagermaid.listener import listener
from pagermaid.services import scheduler
from pagermaid.utils import lang, auto_delete


@listener(
    is_plugin=False, command="reload", need_admin=True, description=lang("reload_des")
)
async def reload_plugins(message: Message):
    """To reload plugins."""
    await reload_all()
    await message.edit(lang("reload_ok"))
    await auto_delete(message, time=10)


@scheduler.scheduled_job("cron", hour="4", id="reload.clear_read_context")
async def clear_read_context_cron():
    read_context.clear()
