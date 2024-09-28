from pagermaid.dependence import sqlite, scheduler, client
from ._bot import bot

__all__ = [
    "bot",
    "sqlite",
    "client",
    "scheduler",
]


def get(name: str):
    data = {
        "Client": bot,
        "SqliteDict": sqlite,
        "AsyncIOScheduler": scheduler,
        "AsyncClient": client,
    }
    return data.get(name)
