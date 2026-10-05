import asyncio
from os import sep
from pathlib import Path
from signal import signal as signal_fn, SIGINT, SIGTERM, SIGABRT
from sys import path, platform, exit

from pyrogram.errors import AuthKeyUnregistered
from pyrogram.handlers import DisconnectHandler

from pagermaid.common.reload import load_all
from pagermaid.config import Config
from pagermaid.dependence import scheduler
from pagermaid.services import bot
from pagermaid.static import working_dir
from pagermaid.utils import lang, logs, SessionFileManager
from pagermaid.web import web
from pagermaid.web.api.web_login import web_login
from pyromod.methods.sign_in_qrcode import start_client

bot.PARENT_DIR = Path(working_dir)
path.insert(1, f"{working_dir}{sep}plugins")

INITIAL_RETRY_DELAY = 5
MAX_RETRY_DELAY = 120
STABLE_RETRY_RESET_AFTER = 300
RETRYABLE_CONNECTION_ERRORS = (
    OSError,
    ConnectionError,
    TimeoutError,
    asyncio.TimeoutError,
)


async def _wait_or_shutdown(awaitable, shutdown_event):
    """Run *awaitable* and return its result, or ``None`` if ``shutdown_event`` fires first.

    Returns ``(completed, result)``:
        completed=True  -> awaitable finished normally; ``result`` is its value.
        completed=False -> shutdown was requested while waiting.
    The pending awaitable is cancelled cleanly in the shutdown case.
    """
    task = asyncio.ensure_future(awaitable)
    stop_task = asyncio.ensure_future(shutdown_event.wait())
    try:
        done, _ = await asyncio.wait(
            {task, stop_task}, return_when=asyncio.FIRST_COMPLETED
        )
        if task in done:
            return True, task.result()
        return False, None
    finally:
        for t in (task, stop_task):
            if not t.done():
                t.cancel()
                try:
                    await t
                except (asyncio.CancelledError, Exception):
                    pass


def _next_delay(delay):
    return min(delay * 2, MAX_RETRY_DELAY)


async def _sleep_for_retry(delay, shutdown_event):
    """Sleep up to *delay* seconds unless shutdown is requested.

    Returns True if we should keep retrying, False if shutdown was requested.
    """
    logs.warning(f"{lang('telegram_retrying')} {delay}s")
    completed, _ = await _wait_or_shutdown(asyncio.sleep(delay), shutdown_event)
    return completed


def _install_signal_handlers(shutdown_event):
    def signal_handler(_, __):
        shutdown_event.set()
        if web.web_server_task:
            web.web_server_task.cancel()

    for s in (SIGINT, SIGTERM, SIGABRT):
        signal_fn(s, signal_handler)


class _LoopState:
    """Result of one iteration step. Keeps the main loop branching trivial."""

    SHUTDOWN = "shutdown"
    RETRY = "retry"
    STOP = "stop"
    CONTINUE = "continue"


async def _try_connect(shutdown_event):
    """Try to (re)connect the bot once.

    Returns one of CONTINUE / SHUTDOWN / RETRY (plus optional error reason).
    """
    logs.info(lang("telegram_connecting"))
    try:
        completed, _ = await _wait_or_shutdown(bot.connect(), shutdown_event)
    except RETRYABLE_CONNECTION_ERRORS as e:
        return _LoopState.RETRY, f"{type(e).__name__}: {e}"
    if not completed:
        return _LoopState.SHUTDOWN, None
    return _LoopState.CONTINUE, None


async def _run_session(shutdown_event):
    """Stay connected until shutdown, restart request, or transient error.

    Returns (state, reason) where state is one of SHUTDOWN / STOP / RETRY.
    """
    reason = None
    loop = asyncio.get_running_loop()
    disconnect_event = asyncio.Event()

    async def _on_disconnect(_client, _):
        loop.call_soon_threadsafe(disconnect_event.set)

    handler = bot.add_handler(DisconnectHandler(_on_disconnect))
    try:
        completed, _ = await _wait_or_shutdown(disconnect_event.wait(), shutdown_event)
    except RETRYABLE_CONNECTION_ERRORS as e:
        reason = f"{type(e).__name__}: {e}"
        completed = True
    finally:
        try:
            bot.remove_handler(*handler)
        except Exception:
            pass

    if not completed:
        return _LoopState.SHUTDOWN, None
    if getattr(bot, "_should_restart", False):
        return _LoopState.STOP, None
    return _LoopState.RETRY, reason


def _log_disconnect(reason):
    if reason:
        logs.warning(f"{lang('telegram_disconnected')}: {reason}")
    else:
        logs.warning(lang("telegram_disconnected"))


async def _reconnect_or_continue(shutdown_event, retry_delay):
    """Ensure the bot is connected. Returns (keep_running, next_retry_delay).

    keep_running=False means the caller should stop the loop entirely.
    """
    if bot.is_connected:
        return True, retry_delay

    state, reason = await _try_connect(shutdown_event)
    if state == _LoopState.CONTINUE:
        return True, retry_delay
    if state == _LoopState.SHUTDOWN:
        return False, retry_delay

    logs.warning(f"{lang('telegram_connection_failed')}: {reason}")
    if not await _sleep_for_retry(retry_delay, shutdown_event):
        return False, retry_delay
    return True, _next_delay(retry_delay)


async def _handle_session_end(state, reason, started_at, retry_delay, shutdown_event):
    """Decide what to do after a session finishes. Returns (keep_running, next_retry_delay)."""
    if state in (_LoopState.SHUTDOWN, _LoopState.STOP):
        return False, retry_delay

    loop = asyncio.get_running_loop()
    if loop.time() - started_at >= STABLE_RETRY_RESET_AFTER:
        retry_delay = INITIAL_RETRY_DELAY

    _log_disconnect(reason)
    if not await _sleep_for_retry(retry_delay, shutdown_event):
        return False, retry_delay
    return True, _next_delay(retry_delay)


async def _run_bot_loop(shutdown_event):
    """Connect to Telegram and stay connected, retrying transient failures."""
    retry_delay = INITIAL_RETRY_DELAY
    loop = asyncio.get_running_loop()

    while not shutdown_event.is_set():
        keep_running, retry_delay = await _reconnect_or_continue(
            shutdown_event, retry_delay
        )
        if not keep_running:
            return
        if not bot.is_connected:
            continue

        started_at = loop.time()
        state, reason = await _run_session(shutdown_event)
        keep_running, retry_delay = await _handle_session_end(
            state, reason, started_at, retry_delay, shutdown_event
        )
        if not keep_running:
            return


async def idle(shutdown_event):
    _install_signal_handlers(shutdown_event)

    if Config.WEB_ENABLE and Config.WEB_LOGIN:
        await shutdown_event.wait()
        return

    await _run_bot_loop(shutdown_event)


async def console_bot(shutdown_event):
    """Initial login flow. Retries transient connection errors until success or shutdown."""
    retry_delay = INITIAL_RETRY_DELAY
    while not shutdown_event.is_set():
        try:
            logs.info(lang("telegram_connecting"))
            await start_client(bot)
            me = await bot.get_me()
            await bot.storage.user_id(me.id)
        except AuthKeyUnregistered:
            logs.error(lang("telegram_auth_key_invalid"))
            SessionFileManager.safe_remove_session()
            exit()
        except RETRYABLE_CONNECTION_ERRORS as e:
            logs.warning(
                f"{lang('telegram_connection_failed')}: {type(e).__name__}: {e}"
            )
            if not await _sleep_for_retry(retry_delay, shutdown_event):
                return
            retry_delay = _next_delay(retry_delay)
            continue

        bot.me = me
        if me.is_bot:
            SessionFileManager.safe_remove_session()
            exit()
        logs.info(f"{lang('save_id')} {me.first_name}({me.id})")
        await load_all()
        return


async def web_bot():
    try:
        await web_login.init()
    except AuthKeyUnregistered:
        logs.error(lang("telegram_auth_key_invalid"))
        SessionFileManager.safe_remove_session()
        exit()
    if bot.me is not None:
        me = await bot.get_me()
        await bot.storage.user_id(me.id)
        if me.is_bot:
            SessionFileManager.safe_remove_session()
            exit()
    else:
        logs.info("Please use web to login, path: web_login .")


async def main():
    logs.info(lang("platform") + platform + lang("platform_load"))
    shutdown_event = web.shutdown_event
    if not scheduler.running:
        scheduler.start()
    bot._loop = asyncio.get_running_loop()
    bot._rebuild_loop_bound_state()
    await web.start()
    try:
        if not (Config.WEB_ENABLE and Config.WEB_LOGIN):
            await console_bot(shutdown_event)
            if shutdown_event.is_set():
                return
            logs.info(lang("start"))
        else:
            await web_bot()
        await idle(shutdown_event)
    finally:
        if scheduler.running:
            scheduler.shutdown()
        try:
            await bot.stop()
        except ConnectionError:
            pass
        if web.web_server:
            try:
                await web.web_server.shutdown()
            except AttributeError:
                pass


bot.run(main())
