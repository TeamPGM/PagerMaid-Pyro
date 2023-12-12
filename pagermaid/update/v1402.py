from pathlib import Path

# move file
# session
session = Path("pagermaid.session")
if session.exists():
    session.rename("data/pagermaid.session")
# config
config = Path("config.yml")
if config.exists():
    config.rename("data/config.yml")
# delete file
# log
log = Path("pagermaid.log.txt")
if log.exists():
    log.unlink()
