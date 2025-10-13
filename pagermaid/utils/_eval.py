import contextlib
import subprocess
import os
import shlex

from importlib.util import find_spec
from sys import executable
from asyncio import create_subprocess_shell
from asyncio.subprocess import PIPE
from typing import Optional

try:
    import pwd
except ImportError:
    pwd = None


async def execute(command, pass_error=True):
    """Executes command and returns output, with the option of enabling stderr."""

    shell_command = None
    if pwd is not None:
        with contextlib.suppress(Exception):
            user_shell = pwd.getpwuid(os.getuid()).pw_shell
            if user_shell:
                shell_command = f"{user_shell} -l -c {shlex.quote(command)}"
    if not shell_command:
        shell_command = command

    executor = await create_subprocess_shell(
        shell_command, stdout=PIPE, stderr=PIPE, stdin=PIPE
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
