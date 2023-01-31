import asyncio
from datetime import datetime, timezone

import psutil
from pydantic import BaseModel
from pagermaid import start_time, Config, pgm_version


class Status(BaseModel):
    version: str
    run_time: str
    cpu_percent: str
    ram_percent: str
    swap_percent: str


async def human_time_duration(seconds) -> str:
    parts = {}
    time_units = (
        ('%m', 60 * 60 * 24 * 30),
        ('%d', 60 * 60 * 24),
        ('%H', 60 * 60),
        ('%M', 60),
        ('%S', 1)
    )
    for unit, div in time_units:
        amount, seconds = divmod(int(seconds), div)
        parts[unit] = str(amount)
    time_form = Config.START_FORM
    for key, value in parts.items():
        time_form = time_form.replace(key, value)
    return time_form


async def get_bot_uptime() -> str:
    current_time = datetime.now(timezone.utc)
    uptime_sec = (current_time - start_time).total_seconds()
    return await human_time_duration(int(uptime_sec))


async def get_status() -> Status:
    uptime = await get_bot_uptime()
    psutil.cpu_percent()
    await asyncio.sleep(0.1)
    cpu_percent = psutil.cpu_percent()
    ram_stat = psutil.virtual_memory()
    swap_stat = psutil.swap_memory()
    return Status(
        version=pgm_version,
        run_time=uptime,
        cpu_percent=f'{cpu_percent}%',
        ram_percent=f'{ram_stat.percent}%',
        swap_percent=f'{swap_stat.percent}%',
    )
