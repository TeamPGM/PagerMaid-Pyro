import ipaddress
import sqlite3

from pydantic import BaseModel, Field
from pathlib import Path

from pagermaid.config import DATA_PATH
from ._path import safe_remove
from ..version import pgm_telethon


class TDSession(BaseModel):
    dc_id: int = Field(default=0)
    api_id: int = Field(default=0)
    test_mode: bool = Field(default=False)
    auth_key: bytes = Field(default=b"")
    date: int = Field(default=0)
    user_id: int = Field(default=0)
    is_bot: bool = Field(default=False)
    server_address_str: str = Field(default="")
    port: int = Field(default=443)

    @property
    def server_address(self):
        if self.server_address_str:
            return self.server_address_str
        test = {
            1: "149.154.175.10",
            2: "149.154.167.40",
            3: "149.154.175.117",
            121: "95.213.217.195",
        }
        prod = {
            1: "149.154.175.53",
            2: "149.154.167.51",
            3: "149.154.175.100",
            4: "149.154.167.91",
            5: "91.108.56.130",
            121: "95.213.217.195",
            203: "91.105.192.100",
        }
        return ipaddress.ip_address(
            test[self.dc_id] if self.test_mode else prod[self.dc_id],
        )


class SessionConvert:
    PYROGRAM_VERSION = 3
    TELETHON_VERSION = 7

    def __init__(self, session: TDSession):
        self.session = session

    @staticmethod
    def is_telethon_file(file: "Path") -> bool:
        if not file.exists():
            return False
        try:
            conn = sqlite3.connect(file, check_same_thread=False)
            version = conn.execute("SELECT version from version;").fetchone()[0]
            conn.close()
            return version >= SessionConvert.TELETHON_VERSION
        except sqlite3.DatabaseError:
            return False

    @staticmethod
    def is_pyrogram_file(file: "Path") -> bool:
        if not file.exists():
            return False
        try:
            conn = sqlite3.connect(file, check_same_thread=False)
            version = conn.execute("SELECT number from version;").fetchone()[0]
            conn.close()
            return version >= SessionConvert.PYROGRAM_VERSION
        except sqlite3.DatabaseError:
            return False

    @classmethod
    def from_pyrogram_file(cls, file) -> "SessionConvert":
        try:
            conn = sqlite3.connect(file, check_same_thread=False)
            version = conn.execute("SELECT number from version;").fetchone()[0]
            selected_session: tuple = conn.execute(
                "SELECT dc_id, test_mode, auth_key, date, user_id, is_bot from sessions;"
            ).fetchone()
        except sqlite3.DatabaseError as err:
            raise ValueError("Invalid Pyrogram session file") from err

        session = TDSession(
            dc_id=selected_session[0],
            test_mode=selected_session[1],
            auth_key=selected_session[2],
            date=selected_session[3],
            user_id=selected_session[4],
            is_bot=selected_session[5],
        )
        if version in (3, 4, 5, 6):
            api_id = conn.execute("SELECT api_id from sessions;").fetchone()[0]
            session.api_id = api_id
        if version in (7,):
            server_address, port = conn.execute(
                "SELECT server_address, port from sessions;"
            ).fetchone()
            session.server_address_str = server_address
            session.port = port
        if version > 7:
            raise ValueError("Invalid pyrogram version")
        conn.close()
        return cls(session)

    @classmethod
    def from_telethon_file(cls, file) -> "SessionConvert":
        try:
            conn = sqlite3.connect(file, check_same_thread=False)
            version = conn.execute("SELECT version from version;").fetchone()[0]
            authorization = conn.execute("SELECT * from sessions;").fetchone()
            conn.close()
        except sqlite3.DatabaseError as err:
            raise ValueError("Invalid Telethon session file") from err

        if version == 7:
            session = TDSession(
                dc_id=authorization[0],
                test_mode=authorization[2] == 80,
                auth_key=authorization[3],
                port=authorization[2],
            )
            cls_obj = cls(session)
            return cls_obj

        else:
            raise ValueError("Invalid telethon version")

    def telethon_file(self, file):
        conn = sqlite3.connect(file, check_same_thread=False)
        conn.execute(
            "CREATE TABLE IF NOT EXISTS version (version INTEGER PRIMARY KEY);"
        )
        conn.execute(
            """CREATE TABLE IF NOT EXISTS sessions (
                    dc_id INTEGER PRIMARY KEY, 
                    server_address TEXT, 
                    port INTEGER, 
                    auth_key BLOB,
                    takeout_id INTEGER
                );
            """
        )
        conn.execute(
            """CREATE TABLE IF NOT EXISTS entities (
                    id integer primary key,
                    hash integer not null,
                    username text,
                    phone integer,
                    name text,
                    date integer
                )"""
        )
        conn.execute(
            """CREATE TABLE IF NOT EXISTS sent_files (
                    md5_digest blob,
                    file_size integer,
                    type integer,
                    id integer,
                    hash integer,
                    primary key(md5_digest, file_size, type)
                )"""
        )
        conn.execute(
            """CREATE TABLE IF NOT EXISTS update_state (
                    id integer primary key,
                    pts integer,
                    qts integer,
                    date integer,
                    seq integer
                )"""
        )
        conn.execute("INSERT INTO version VALUES (?);", (self.TELETHON_VERSION,))
        conn.execute(
            "INSERT INTO sessions VALUES (?, ?, ?, ?, ?);",
            (
                self.session.dc_id,
                str(self.session.server_address),
                self.session.port,
                self.session.auth_key,
                0,
            ),
        )
        conn.commit()
        conn.close()
        return file

    def pyrogram_file(self, file, **kwargs):
        conn = sqlite3.connect(file, check_same_thread=False)
        schema = """
            CREATE TABLE sessions
            (
                dc_id     INTEGER PRIMARY KEY,
                api_id    INTEGER,
                test_mode INTEGER,
                auth_key  BLOB,
                date      INTEGER NOT NULL,
                user_id   INTEGER,
                is_bot    INTEGER
            );
            CREATE TABLE peers
            (
                id             INTEGER PRIMARY KEY,
                access_hash    INTEGER,
                type           INTEGER NOT NULL,
                username       TEXT,
                phone_number   TEXT,
                last_update_on INTEGER NOT NULL DEFAULT (CAST(STRFTIME('%s', 'now') AS INTEGER))
            );
            CREATE TABLE version
            (
                number INTEGER PRIMARY KEY
            );
            CREATE INDEX idx_peers_id ON peers (id);
            CREATE INDEX idx_peers_username ON peers (username);
            CREATE INDEX idx_peers_phone_number ON peers (phone_number);
            CREATE TRIGGER trg_peers_last_update_on
                AFTER UPDATE
                ON peers
            BEGIN
                UPDATE peers
                SET last_update_on = CAST(STRFTIME('%s', 'now') AS INTEGER)
                WHERE id = NEW.id;
            END;
        """
        conn.executescript(schema)
        conn.execute("INSERT INTO version VALUES (?)", (self.PYROGRAM_VERSION,))
        conn.execute(
            "INSERT INTO sessions VALUES (?, ?, ?, ?, ?, ?, ?)",
            (2, None, None, None, 0, None, None),
        )
        for key, value in {
            "dc_id": self.session.dc_id,
            "api_id": int(kwargs.get("api_id", 0)) or self.session.api_id,
            "test_mode": self.session.test_mode,
            "auth_key": self.session.auth_key,
            "date": 0,
            "user_id": int(kwargs.get("user_id", 0)) or self.session.user_id,
            "is_bot": bool(kwargs.get("is_bot")) or self.session.is_bot,
        }.items():
            conn.execute(f"UPDATE sessions SET {key} = ?", (value,))
        conn.commit()
        conn.close()
        return True


class SessionFileManager:
    SESSION_PATH = DATA_PATH / "pagermaid.session"
    SESSION_TELETHON_PATH = DATA_PATH / "pagermaid_telethon.session"
    SESSION_PYROGRAM_PATH = DATA_PATH / "pagermaid_pyrogram.session"
    REAL_SESSION_PATH = None

    @staticmethod
    def get_session_file_path() -> "Path":
        """Get the path to the session file."""
        if SessionFileManager.REAL_SESSION_PATH is None:
            if pgm_telethon:
                SessionFileManager.REAL_SESSION_PATH = (
                    SessionFileManager.get_session_file_path_telethon()
                )
            else:
                SessionFileManager.REAL_SESSION_PATH = (
                    SessionFileManager.get_session_file_path_pyrogram()
                )
        return SessionFileManager.REAL_SESSION_PATH

    @staticmethod
    def get_session_file_stem() -> str:
        """Get the stem of the session file."""
        return SessionFileManager.get_session_file_path().stem

    @staticmethod
    def get_session_file_path_telethon() -> "Path":
        """Determines the appropriate session file path for Telethon."""
        if SessionConvert.is_telethon_file(SessionFileManager.SESSION_TELETHON_PATH):
            return SessionFileManager.SESSION_TELETHON_PATH
        if SessionConvert.is_telethon_file(SessionFileManager.SESSION_PATH):
            return SessionFileManager.SESSION_PATH
        for session_path in [
            SessionFileManager.SESSION_PATH,
            SessionFileManager.SESSION_PYROGRAM_PATH,
        ]:
            if SessionConvert.is_pyrogram_file(session_path):
                session_manager = SessionConvert.from_pyrogram_file(session_path)
                session_manager.telethon_file(SessionFileManager.SESSION_TELETHON_PATH)
                return SessionFileManager.SESSION_TELETHON_PATH
        return SessionFileManager.SESSION_PATH

    @staticmethod
    def get_session_file_path_pyrogram() -> "Path":
        """Determines the appropriate session file path for Pyrogram."""
        if SessionConvert.is_pyrogram_file(SessionFileManager.SESSION_PYROGRAM_PATH):
            return SessionFileManager.SESSION_PYROGRAM_PATH
        if SessionConvert.is_pyrogram_file(SessionFileManager.SESSION_PATH):
            return SessionFileManager.SESSION_PATH
        for session_path in [
            SessionFileManager.SESSION_PATH,
            SessionFileManager.SESSION_TELETHON_PATH,
        ]:
            if SessionConvert.is_telethon_file(session_path):
                session_manager = SessionConvert.from_telethon_file(session_path)
                session_manager.session.user_id = 777000
                session_manager.pyrogram_file(SessionFileManager.SESSION_PYROGRAM_PATH)
                return SessionFileManager.SESSION_PYROGRAM_PATH
        return SessionFileManager.SESSION_PATH

    @staticmethod
    def safe_remove_session():
        """Safely remove the session file."""
        if SessionFileManager.REAL_SESSION_PATH is None:
            return
        safe_remove(SessionFileManager.REAL_SESSION_PATH)
