import contextlib
import io
import sys
import traceback
from typing import Optional, TYPE_CHECKING

from pagermaid.services import client as httpx_client, bot, sqlite
from pagermaid.utils import lang
from pagermaid.utils.listener import from_self

if TYPE_CHECKING:
    from pagermaid.enums import Message


async def run_eval(cmd: str, message=None) -> str:
    old_stderr = sys.stderr
    old_stdout = sys.stdout
    redirected_output = sys.stdout = io.StringIO()
    redirected_error = sys.stderr = io.StringIO()
    stdout, stderr, exc = None, None, None
    try:
        await aexec(cmd, message, bot)
    except Exception:  # noqa
        exc = traceback.format_exc()
    stdout = redirected_output.getvalue()
    stderr = redirected_error.getvalue()
    sys.stdout = old_stdout
    sys.stderr = old_stderr
    if exc:
        evaluation = exc
    elif stderr:
        evaluation = stderr
    elif stdout:
        evaluation = stdout
    else:
        evaluation = "Success"
    return evaluation


async def aexec(code, event, client):
    text = (
        (
            ("async def __aexec(e, client): " + "\n msg = message = e")
            + "\n reply = message.reply_to_message if message else None"
        )
        + "\n chat = e.chat if e else None"
    ) + "".join(f"\n {x}" for x in code.split("\n"))
    if sys.version_info >= (3, 13):
        local = {}
        exec(text, globals(), local)
    else:
        exec(text)
        local = locals()

    return await local["__aexec"](event, client)


async def paste_pb(
    content: str, private: bool = True, sunset: int = 3600
) -> Optional[str]:
    data = {
        "c": content,
    }
    if private:
        data["p"] = "1"
    if sunset:
        data["sunset"] = sunset
    result = await httpx_client.post("https://fars.ee", data=data)
    if result.is_error:
        return None
    return result.headers.get("location")


async def process_exit(start: int, _client, message=None):
    if message:
        sqlite["exit_msg"] = {"cid": message.chat.id, "mid": message.id}
        return
    data = sqlite.get("exit_msg", {})
    cid, mid = data.get("cid", 0), data.get("mid", 0)
    if start and data and cid and mid:
        with contextlib.suppress(Exception):
            msg: "Message" = await _client.get_messages(cid, mid)
            if msg:
                await msg.edit(
                    (
                        (msg.text or msg.caption)
                        if from_self(msg) and (msg.text or msg.caption)
                        else ""
                    )
                    + f"\n\n> {lang('restart_complete')}"
                )
        del sqlite["exit_msg"]
