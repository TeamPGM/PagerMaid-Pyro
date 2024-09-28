from sqlitedict import SqliteDict

from pagermaid.config import DATA_PATH

sqlite_path = DATA_PATH / "data.sqlite"
sqlite = SqliteDict(sqlite_path, autocommit=True)


def get_sudo_list():
    return sqlite.get("sudo_list", [])


def status_sudo():
    return sqlite.get("sudo_enable", False)
