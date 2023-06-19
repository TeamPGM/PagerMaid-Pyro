from pagermaid import bot
from pagermaid import logs
from pagermaid.single_utils import sqlite
from pagermaid.scheduler import scheduler
from pagermaid.utils import client


def get(name: str):
    data = {
        "Client": bot,
        "Logger": logs,
        "SqliteDict": sqlite,
        "AsyncIOScheduler": scheduler,
        "AsyncClient": client,
    }
    return data.get(name)
