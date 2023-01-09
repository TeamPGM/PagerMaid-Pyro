""" PagerMaid module that contains utilities related to system status. """

import re

from datetime import datetime, timezone
from platform import uname, python_version
from sys import platform

from pyrogram import __version__
from pyrogram.enums import ChatType
from pyrogram.raw.functions import Ping
from pyrogram.enums.parse_mode import ParseMode

from getpass import getuser
from socket import gethostname
from time import time
from psutil import boot_time, virtual_memory, disk_partitions
from shutil import disk_usage
from subprocess import Popen, PIPE

from pagermaid import start_time, Config, pgm_version
from pagermaid.enums import Client, Message
from pagermaid.listener import listener
from pagermaid.utils import lang, execute

DCs = {
    1: "149.154.175.50",
    2: "149.154.167.51",
    3: "149.154.175.100",
    4: "149.154.167.91",
    5: "91.108.56.130"
}


@listener(is_plugin=False, command="sysinfo",
          description=lang('sysinfo_des'))
async def sysinfo(message: Message):
    """ Retrieve system information via neofetch. """
    if not Config.SILENT:
        message = await message.edit(lang("sysinfo_loading"))
    if platform == 'win32':
        return await message.edit(neofetch_win(), parse_mode=ParseMode.HTML)
    result = await execute("neofetch --config none --stdout")
    await message.edit(f"`{result}`")


@listener(is_plugin=False, command="status",
          description=lang('status_des'))
async def status(message: Message):
    # database
    # database = lang('status_online') if redis_status() else lang('status_offline')
    # uptime https://gist.github.com/borgstrom/936ca741e885a1438c374824efb038b3
    time_units = (
        ('%m', 60 * 60 * 24 * 30),
        ('%d', 60 * 60 * 24),
        ('%H', 60 * 60),
        ('%M', 60),
        ('%S', 1)
    )

    async def human_time_duration(seconds):
        parts = {}
        for unit, div in time_units:
            amount, seconds = divmod(int(seconds), div)
            parts[unit] = str(amount)
        time_form = Config.START_FORM
        for key, value in parts.items():
            time_form = time_form.replace(key, value)
        return time_form

    current_time = datetime.now(timezone.utc)
    uptime_sec = (current_time - start_time).total_seconds()
    uptime = await human_time_duration(int(uptime_sec))
    text = (f"**{lang('status_hint')}** \n"
            f"{lang('status_name')}: `{uname().node}` \n"
            f"{lang('status_platform')}: `{platform}` \n"
            f"{lang('status_release')}: `{uname().release}` \n"
            f"{lang('status_python')}: `{python_version()}` \n"
            f"{lang('status_pyrogram')}: `{__version__}` \n"
            f"{lang('status_pgm')}: `{pgm_version}`\n"
            f"{lang('status_uptime')}: `{uptime}`"
            )
    await message.edit(text)


@listener(is_plugin=False, command="stats",
          description=lang("stats_des"))
async def stats(client: Client, message: Message):
    msg = await message.edit(lang("stats_loading"))
    a, u, g, s, c, b = 0, 0, 0, 0, 0, 0
    async for dialog in client.get_dialogs():
        chat_type = dialog.chat.type
        if chat_type == ChatType.BOT:
            b += 1
        elif chat_type == ChatType.PRIVATE:
            u += 1
        elif chat_type == ChatType.GROUP:
            g += 1
        elif chat_type == ChatType.SUPERGROUP:
            s += 1
        elif chat_type == ChatType.CHANNEL:
            c += 1
        a += 1
    text = (f"**{lang('stats_hint')}** \n"
            f"{lang('stats_dialogs')}: `{a}` \n"
            f"{lang('stats_private')}: `{u}` \n"
            f"{lang('stats_group')}: `{g}` \n"
            f"{lang('stats_supergroup')}: `{s}` \n"
            f"{lang('stats_channel')}: `{c}` \n"
            f"{lang('stats_bot')}: `{b}`"
            )
    await msg.edit(text)


@listener(is_plugin=False, command="pingdc",
          description=lang("pingdc_des"))
async def ping_dc(message: Message):
    """ Ping your or other data center's IP addresses. """
    data = []
    print("1")
    for dc in range(1, 6):
        if platform == "win32":
            result = await execute(f'ping -n 1 {DCs[dc]} | find "最短"')
            if result := re.findall(r"= (.*?)ms", result or ""):
                data.append(result[0])
            else:
                data.append("0")
        else:
            result = await execute(f"ping -c 1 {DCs[dc]} | awk -F '/' " + "'END {print $5}'")
            try:
                data.append(str(float(result)))
            except ValueError:
                data.append("0")
    await message.edit(
        f"{lang('pingdc_1')}: `{data[0]}ms`\n"
        f"{lang('pingdc_2')}: `{data[1]}ms`\n"
        f"{lang('pingdc_3')}: `{data[2]}ms`\n"
        f"{lang('pingdc_4')}: `{data[3]}ms`\n"
        f"{lang('pingdc_5')}: `{data[4]}ms`"
    )


@listener(is_plugin=False, command="ping",
          description=lang("ping_des"))
async def ping(client: Client, message: Message):
    """ Calculates latency between PagerMaid and Telegram. """
    start = datetime.now()
    await client.invoke(Ping(ping_id=0))
    end = datetime.now()
    ping_duration = (end - start).microseconds / 1000
    start = datetime.now()
    message = await message.edit("Pong!")
    end = datetime.now()
    msg_duration = (end - start).microseconds / 1000
    await message.edit(f"Pong!| PING: {ping_duration} | MSG: {msg_duration}")


def wmic(command: str):
    """ Fetch the wmic command to cmd """
    try:
        p = Popen(command.split(" "), stdout=PIPE)
    except FileNotFoundError:
        return r"WMIC.exe was not found... Make sure 'C:\Windows\System32\wbem' is added to PATH."

    stdout, stderror = p.communicate()

    output = stdout.decode("gbk", "ignore")
    lines = output.split("\r\r")
    lines = [g.replace("\n", "").replace("  ", "") for g in lines if len(g) > 2]
    return lines


def get_uptime():
    """ Get the device uptime """
    delta = round(time() - boot_time())

    hours, remainder = divmod(int(delta), 3600)
    minutes, seconds = divmod(remainder, 60)
    days, hours = divmod(hours, 24)

    def include_s(text: str, num: int):
        return f"{num} {text}{'' if num == 1 else 's'}"

    d = include_s("day", days)
    h = include_s("hour", hours)
    m = include_s("minute", minutes)
    s = include_s("second", seconds)

    if days:
        output = f"{d}, {h}, {m} and {s}"
    elif hours:
        output = f"{h}, {m} and {s}"
    elif minutes:
        output = f"{m} and {s}"
    else:
        output = s

    return output


def readable(num, suffix='B'):
    """ Convert Bytes into human-readable formats """
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


def get_ram():
    """ Get RAM used/free/total """
    ram = virtual_memory()
    used = readable(ram.used)
    total = readable(ram.total)

    percent_used = round(ram.used / ram.total * 100, 2)

    return f"{used} / {total} ({percent_used}%)"


def partitions():
    """ Find the disk partitions on current OS """
    parts = disk_partitions()
    listparts = []

    for g in parts:
        try:
            total, used, free = disk_usage(g.device)
            percent_used = round(used / total * 100, 2)
            listparts.append(f"      {g.device[:2]} {readable(used)} / {readable(total)} ({percent_used}%)")
        except PermissionError:
            continue

    return listparts


def neofetch_win():
    user_name = getuser()
    host_name = gethostname()
    os = wmic("wmic os get Caption")[-1].replace("Microsoft ", "")
    uptime = get_uptime()
    mboard_name = wmic("wmic baseboard get Manufacturer")
    mboard_module = wmic("wmic baseboard get product")
    try:
        mboard = f"{mboard_name[-1]} ({mboard_module[-1]})"
    except IndexError:
        mboard = "Unknown..."
    cpu = wmic("wmic cpu get name")[-1]
    gpu = wmic("wmic path win32_VideoController get name")
    gpu = [f'     {g.strip()}' for g in gpu[1:]][0].strip()
    ram = get_ram()
    disks = '\n'.join(partitions())
    return (
        f'<code>{user_name}@{host_name}\n---------\nOS: {os}\nUptime: {uptime}\n'
        f'Motherboard: {mboard}\nCPU: {cpu}\nGPU: {gpu}\nMemory: {ram}\n'
        f'Disk:\n{disks}</code>'
    )
