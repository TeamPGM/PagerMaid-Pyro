from datetime import datetime
from pathlib import Path
import shutil

data = Path("data")
data.mkdir(exist_ok=True)


def rename(old: Path, need_backup: bool = True):
    if old.exists():
        old_file_name = old.name
        new = data / old_file_name
        if need_backup and new.exists():
            datetime_str = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
            backup = data / (new.stem + f".{datetime_str}" + new.suffix)
            shutil.move(new, backup)
        shutil.move(old, new)


# move file
# session
session = Path("pagermaid.session")
rename(session)
# config
config = Path("config.yml")
rename(config)
# docker
docker = Path("install.lock")
rename(docker, need_backup=False)
# delete file
# log
log = Path("pagermaid.log.txt")
if log.exists():
    log.unlink()
