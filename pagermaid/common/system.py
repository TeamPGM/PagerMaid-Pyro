import io
import sys
import traceback

from pagermaid import bot


async def run_eval(cmd: str, message=None, only_result: bool = False) -> str:
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
    return evaluation if only_result else f"**>>>** `{cmd}` \n`{evaluation}`"


async def aexec(code, event, client):
    exec(
        (
                (
                        ("async def __aexec(e, client): " + "\n msg = message = e")
                        + "\n reply = message.reply_to_message if message else None"
                )
                + "\n chat = e.chat if e else None"
        )
        + "".join(f"\n {x}" for x in code.split("\n"))
    )

    return await locals()["__aexec"](event, client)
