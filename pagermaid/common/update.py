from sys import executable

from pagermaid.utils import execute


async def update(force: bool = False):
    await execute("git fetch --all")
    if force:
        await execute("git reset --hard origin/master")
    await execute("git pull --all")
    await execute(f"{executable} -m pip install --upgrade -r requirements.txt")
    await execute(f"{executable} -m pip install -r requirements.txt")
