import pyromod.listen
from pyrogram import Client

from pagermaid.config import Config
from pagermaid.version import pgm_version

bot = Client(
    "pagermaid",
    session_string=Config.STRING_SESSION,
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    ipv6=Config.IPV6,
    proxy=Config.PROXY,
    app_version=f"PGP {pgm_version}",
    workdir="data",
)
