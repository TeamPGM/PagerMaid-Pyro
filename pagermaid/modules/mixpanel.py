import contextlib
import datetime
import json
import random
import time
import uuid
from asyncio import sleep
from typing import Union

from pyrogram.raw.functions.messages import (
    GetSponsoredMessages,
    ViewSponsoredMessage,
    ClickSponsoredMessage,
)
from pyrogram.raw.types import InputPeerChannel
from pyrogram.raw.types.messages import SponsoredMessages, SponsoredMessagesEmpty

from pagermaid.config import Config
from pagermaid.enums import Client, Message
from pagermaid.hook import Hook
from pagermaid.services import client as request, scheduler, bot as userbot
from pagermaid.utils import logs


class DatetimeSerializer(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            fmt = "%Y-%m-%dT%H:%M:%S"
            return obj.strftime(fmt)

        return json.JSONEncoder.default(self, obj)


class Mixpanel:
    def __init__(self, token: str):
        self._token = token
        self._serializer = DatetimeSerializer
        self._request = request
        self.api_host = "api.mixpanel.com"
        self.is_people_set = False

    @staticmethod
    def _now():
        return time.time()

    @staticmethod
    def _make_insert_id():
        return uuid.uuid4().hex

    @staticmethod
    def json_dumps(data, cls=None):
        # Separators are specified to eliminate whitespace.
        return json.dumps(data, separators=(",", ":"), cls=cls)

    async def api_call(self, endpoint, json_message):
        _endpoints = {
            "events": f"https://{self.api_host}/track",
            "people": f"https://{self.api_host}/engage",
        }
        request_url = _endpoints.get(endpoint)
        if request_url is None:
            return
        params = {
            "data": json_message,
            "verbose": 1,
            "ip": 0,
        }
        start = self._now()
        with contextlib.suppress(Exception):
            await self._request.post(request_url, data=params, timeout=10.0)
        logs.debug(f"Mixpanel request took {self._now() - start} seconds")

    async def people_set(
        self, distinct_id: str, properties: dict, force_update: bool = False
    ):
        if self.is_people_set and (not force_update):
            return
        message = {
            "$distinct_id": distinct_id,
            "$set": properties,
        }
        record = {"$token": self._token, "$time": self._now()}
        # sourcery skip: dict-assign-update-to-union
        record.update(message)
        res = await self.api_call(
            "people", self.json_dumps(record, cls=self._serializer)
        )
        self.is_people_set = True
        return res

    async def track(self, distinct_id: str, event_name: str, properties: dict):
        all_properties = {
            "token": self._token,
            "distinct_id": distinct_id,
            "time": self._now(),
            "$insert_id": self._make_insert_id(),
            "mp_lib": "python",
            "$lib_version": "4.10.0",
        }
        if properties:
            # sourcery skip: dict-assign-update-to-union
            all_properties.update(properties)
        event = {
            "event": event_name,
            "properties": all_properties,
        }
        return await self.api_call(
            "events", self.json_dumps(event, cls=self._serializer)
        )


mp = Mixpanel(Config.MIXPANEL_API)


async def set_people(bot: Client, force_update: bool = False):
    if not Config.ALLOW_ANALYTIC:
        return
    if mp.is_people_set and (not force_update):
        return
    if not bot.me:
        bot.me = await bot.get_me()
    data = {"$first_name": bot.me.first_name, "is_premium": bot.me.is_premium}
    if bot.me.username:
        data["username"] = bot.me.username
    bot.loop.create_task(mp.people_set(str(bot.me.id), data, force_update=force_update))


@Hook.on_startup()
async def mixpanel_init_id(bot: Client):
    if not Config.ALLOW_ANALYTIC:
        return
    await set_people(bot)
    add_log_sponsored_clicked_task()
    await log_sponsored_clicked()


@Hook.command_postprocessor()
async def mixpanel_report(bot: Client, message: Message, command, sub_command):
    if not Config.ALLOW_ANALYTIC:
        return
    await set_people(bot)
    if not bot.me:
        bot.me = await bot.get_me()
    sender_id = message.from_user.id if message.from_user else ""
    sender_id = message.sender_chat.id if message.sender_chat else sender_id
    if sender_id < 0 and message.outgoing:
        sender_id = bot.me.id
    properties = {"command": command, "bot_id": bot.me.id}
    if sub_command:
        properties["sub_command"] = sub_command
    bot.loop.create_task(
        mp.track(
            str(sender_id),
            f"Function {command}",
            properties,
        )
    )


async def get_sponsored(
    bot: Client, channel: "InputPeerChannel"
) -> Union["SponsoredMessages", "SponsoredMessagesEmpty"]:
    result = await bot.invoke(GetSponsoredMessages(peer=channel))
    logs.debug(f"Get sponsored messages: {type(result)}")
    return result


async def read_sponsored(
    bot: Client, channel: "InputPeerChannel", random_id: bytes
) -> bool:
    result = await bot.invoke(ViewSponsoredMessage(peer=channel, random_id=random_id))
    if result:
        bot.loop.create_task(
            mp.track(
                str(bot.me.id),
                "Sponsored Read",
                {"channel_id": channel.channel_id, "bot_id": bot.me.id},
            )
        )
    logs.debug(f"Read sponsored message {random_id}: {result}")
    return result


async def click_sponsored(
    bot: Client, channel: "InputPeerChannel", random_id: bytes
) -> bool:
    result = await bot.invoke(ClickSponsoredMessage(peer=channel, random_id=random_id))
    if result:
        bot.loop.create_task(
            mp.track(
                str(bot.me.id),
                "Sponsored Click",
                {"channel_id": channel.channel_id, "bot_id": bot.me.id},
            )
        )
    logs.debug(f"Click sponsored message {random_id}: {result}")
    return result


async def log_sponsored_clicked_one(username: str):
    channel = await userbot.resolve_peer(username)
    sponsored = await get_sponsored(userbot, channel)
    if isinstance(sponsored, SponsoredMessagesEmpty):
        return
    for message in sponsored.messages:
        await sleep(random.randint(1, 5))
        if message.random_id:
            with contextlib.suppress(Exception):
                await read_sponsored(userbot, channel, message.random_id)
            await sleep(random.randint(1, 5))
            with contextlib.suppress(Exception):
                await click_sponsored(userbot, channel, message.random_id)


async def log_sponsored_clicked():
    if not Config.ALLOW_ANALYTIC:
        return
    await set_people(userbot)
    if not userbot.me:
        userbot.me = await userbot.get_me()
    if (not userbot.me) or userbot.me.is_premium:
        return
    for username in ["PagerMaid_Modify"]:
        await log_sponsored_clicked_one(username)


def add_log_sponsored_clicked_task():
    # run random time between 1 and 5 hours
    scheduler.add_job(log_sponsored_clicked, "interval", hours=random.randint(1, 5))
