import contextlib
from typing import TYPE_CHECKING

from pyrogram import filters
from pyrogram.errors import RPCError

from pagermaid.dependence import status_sudo, get_sudo_list, sqlite
from pagermaid.group_manager import enforce_permission
from ._config_utils import lang

if TYPE_CHECKING:
    from pagermaid.enums import Message


def get_permission_name(is_plugin: bool, need_admin: bool, command: str) -> str:
    """Get permission name."""
    if is_plugin:
        return f"plugins_root.{command}" if need_admin else f"plugins.{command}"
    else:
        return f"system.{command}" if need_admin else f"modules.{command}"


def sudo_filter(permission: str):
    async def if_sudo(flt, _, message: "Message"):
        if not status_sudo():
            return False
        try:
            from_id = (
                message.from_user.id if message.from_user else message.sender_chat.id
            )
            sudo_list = get_sudo_list()
            if from_id not in sudo_list:
                if message.chat.id in sudo_list:
                    return enforce_permission(message.chat.id, flt.permission)
                return False
            return enforce_permission(from_id, flt.permission)
        except Exception:  # noqa
            return False

    return filters.create(if_sudo, permission=permission)


def from_self(message: "Message") -> bool:
    if message.outgoing:
        return True
    return message.from_user.is_self if message.from_user else False


def from_msg_get_sudo_uid(message: "Message") -> int:
    """Get the sudo uid from the message."""
    from_id = message.from_user.id if message.from_user else message.sender_chat.id
    return from_id if from_id in get_sudo_list() else message.chat.id


def check_manage_subs(message: "Message") -> bool:
    return from_self(message) or enforce_permission(
        from_msg_get_sudo_uid(message), "modules.manage_subs"
    )


async def process_exit(start: int, _client, message=None):
    data = sqlite.get("exit_msg", {})
    cid, mid = data.get("cid", 0), data.get("mid", 0)
    if start and data and cid and mid:
        with contextlib.suppress(Exception):
            msg: "Message" = await _client.get_messages(cid, mid)
            if msg:
                await msg.edit(
                    (
                        (msg.text or msg.caption)
                        if msg.from_user.is_self and (msg.text or msg.caption)
                        else ""
                    )
                    + f'\n\n> {lang("restart_complete")}'
                )
        del sqlite["exit_msg"]
    if message:
        sqlite["exit_msg"] = {"cid": message.chat.id, "mid": message.id}


def format_exc(e: BaseException) -> str:
    if isinstance(e, RPCError):
        return f"<code>API [{e.CODE} {e.ID or e.NAME}] — {e.MESSAGE.format(value=e.value)}</code>"
    return f"<code>{e.__class__.__name__}: {e}</code>"
