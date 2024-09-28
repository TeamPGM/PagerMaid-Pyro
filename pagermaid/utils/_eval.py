import subprocess
from importlib.util import find_spec
from sys import executable
from asyncio import create_subprocess_shell
from asyncio.subprocess import PIPE
from typing import Optional


async def execute(command, pass_error=True):
    """Executes command and returns output, with the option of enabling stderr."""
    executor = await create_subprocess_shell(
        command, stdout=PIPE, stderr=PIPE, stdin=PIPE
    )

    stdout, stderr = await executor.communicate()
    if pass_error:
        try:
            result = str(stdout.decode().strip()) + str(stderr.decode().strip())
        except UnicodeDecodeError:
            result = str(stdout.decode("gbk").strip()) + str(
                stderr.decode("gbk").strip()
            )
    else:
        try:
            result = str(stdout.decode().strip())
        except UnicodeDecodeError:
            result = str(stdout.decode("gbk").strip())
    return result


def pip_install(
    package: str, version: Optional[str] = "", alias: Optional[str] = ""
) -> bool:
    """Auto install extra pypi packages"""
    if not alias:
        # when import name is not provided, use package name
        alias = package
    if find_spec(alias) is None:
        subprocess.call([executable, "-m", "pip", "install", f"{package}{version}"])
        if find_spec(package) is None:
            return False
    return True
