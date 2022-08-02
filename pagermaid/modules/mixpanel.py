from pagermaid import Config
from pagermaid.enums import Client, Message
from pagermaid.hook import Hook

from mixpanel import Mixpanel
from mixpanel_async import AsyncBufferedConsumer

mp = Mixpanel(Config.MIXPANEL_API, consumer=AsyncBufferedConsumer())


@Hook.on_startup()
async def mixpanel_init_id(bot: Client):
    me = await bot.get_me()
    if me.username:
        mp.people_set(str(me.id), {'$first_name': me.first_name, "username": me.username})
    else:
        mp.people_set(str(me.id), {'$first_name': me.first_name})


@Hook.command_postprocessor()
async def mixpanel_report(bot: Client, message: Message, command):
    if not Config.ALLOW_ANALYTIC:
        return
    me = await bot.get_me()
    sender_id = message.from_user.id if message.from_user else ""
    sender_id = message.sender_chat.id if message.sender_chat else sender_id
    if sender_id < 0 and message.outgoing:
        sender_id = me.id
    mp.track(str(sender_id), f'Function {command}', {'command': command, "bot_id": me.id})
