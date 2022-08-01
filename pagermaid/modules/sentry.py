import sentry_sdk

from subprocess import run, PIPE
from time import time

from pyrogram.errors import Unauthorized

from pagermaid import Config
from pagermaid.enums import Client, Message
from pagermaid.hook import Hook
from pagermaid.single_utils import safe_remove


def sentry_before_send(event, hint):
    global sentry_sdk_report_time
    exc_info = hint.get("exc_info")
    if exc_info and isinstance(exc_info[1], Unauthorized):
        # The user has been deleted/deactivated or session revoked
        safe_remove('pagermaid.session')
        exit(1)
    if time() <= sentry_sdk_report_time + 30:
        sentry_sdk_report_time = time()
        return None
    else:
        sentry_sdk_report_time = time()
        return event


sentry_sdk_report_time = time()
sentry_sdk_git_hash = run("git rev-parse HEAD", stdout=PIPE, shell=True).stdout.decode().strip()
sentry_sdk.init(
    Config.SENTRY_API,
    traces_sample_rate=1.0,
    release=sentry_sdk_git_hash,
    before_send=sentry_before_send,
    environment="production",
)


@Hook.on_startup()
async def sentry_init_id(bot: Client):
    me = await bot.get_me()
    if me.username:
        sentry_sdk.set_user({"id": me.id, "name": me.first_name, "username": me.username, "ip_address": "{{auto}}"})
    else:
        sentry_sdk.set_user({"id": me.id, "name": me.first_name, "ip_address": "{{auto}}"})


@Hook.process_error()
async def sentry_report(message: Message, command, exc_info, **_):
    sender_id = message.from_user.id if message.from_user else ""
    sender_id = message.sender_chat.id if message.sender_chat else sender_id
    sentry_sdk.set_context("Target", {"ChatID": str(message.chat.id),
                                      "UserID": str(sender_id),
                                      "Msg": message.text or ""})
    if command:
        sentry_sdk.set_tag("com", command)
    sentry_sdk.capture_exception(exc_info)
