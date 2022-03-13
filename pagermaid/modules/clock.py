""" This module handles world clock related utility. """

from datetime import datetime

from pyrogram import Client
from pytz import country_names, country_timezones, timezone
from pagermaid.config import Config
from pagermaid.listener import listener
from pagermaid.utils import lang, alias_command, Message


@listener(is_plugin=False, outgoing=True, command=alias_command('time'),
          description=lang('time_des'),
          parameters=lang('time_parameters'))
async def time(client: Client, message: Message):
    """ For querying time. """
    if len(message.parameter) == 1:
        country = message.parameter[0].title()
    else:
        country = Config.REGION
    try:
        time_form = Config.TIME_FORM
        date_form = Config.DATE_FORM
        datetime.now().strftime(time_form)
        datetime.now().strftime(date_form)
    except (ValueError, KeyError):
        time_form = "%H:%M"
        date_form = "%A %y/%m/%d"
    if not country:
        time_zone = await get_timezone(Config.REGION)
        await message.edit(
            f"**{Config.REGION} {lang('time_time')}：**\n"
            f"`{datetime.now(time_zone).strftime(date_form)} "
            f"{datetime.now(time_zone).strftime(time_form)}`"
        )
        return

    time_zone = await get_timezone(country)
    if not time_zone:
        if len(message.parameter) < 1:
            await message.edit(lang('time_config'))
            return
        try:
            time_num, utc_num = int(message.parameter[0]), int(message.parameter[0])
            if time_num == 0:
                time_num, utc_num = '', ''
            elif 0 < time_num < 13:
                time_num, utc_num = f'-{time_num}', f'+{time_num}'
            elif -13 < time_num < 0:
                time_num, utc_num = f'+{-time_num}', f'{time_num}'
            elif time_num < -12:
                time_num, utc_num = '+12', '-12'
            elif time_num > 12:
                time_num, utc_num = '-12', '+12'
            time_zone = timezone(f'Etc/GMT{time_num}')
            country_name = f'UTC{utc_num}'
        except ValueError:
            await message.edit(lang('arg_error'))
            return
    else:
        try:
            country_name = country_names[country]
        except KeyError:
            country_name = country

    await message.edit(f"**{country_name} {lang('time_time')}：**\n"
                       f"`{datetime.now(time_zone).strftime(date_form)} "
                       f"{datetime.now(time_zone).strftime(time_form)}`")


async def get_timezone(target):
    """ Returns timezone of the parameter in command. """
    if "(Uk)" in target:
        target = target.replace("Uk", "UK")
    if "(Us)" in target:
        target = target.replace("Us", "US")
    if " Of " in target:
        target = target.replace(" Of ", " of ")
    if "(Western)" in target:
        target = target.replace("(Western)", "(western)")
    if "Minor Outlying Islands" in target:
        target = target.replace("Minor Outlying Islands", "minor outlying islands")
    if "Nl" in target:
        target = target.replace("Nl", "NL")

    for country_code in country_names:
        if target == country_names[country_code]:
            return timezone(country_timezones[country_code][0])
    try:
        if country_names[target]:
            return timezone(country_timezones[target][0])
    except KeyError:
        return
