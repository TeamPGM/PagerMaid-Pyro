import subprocess
import os
import shlex
import pwd

from importlib.util import find_spec
from sys import executable
from asyncio import create_subprocess_shell
from asyncio.subprocess import PIPE
from typing import Optional


async def execute(command, pass_error=True):
    """Executes command and returns output, with the option of enabling stderr."""

    # Attempt to obtain the current user's default shell from /etc/passwd.
    # If this fails for any reason, fall back to the standard /bin/sh.
    # The chosen shell is then launched in login mode (-l) to initialize
    # the user's environment, including system-wide and user-specific shell
    # configuration files such as /etc/profile, ~/.bash_profile, and ~/.bashrc
    # Finally, the shell executes the given command (-c) with proper quoting
    # to avoid shell injection issues.
    # 
    # TLDR; 
    # This allows the executed command to automatically load the user's shell environment variables.
    try:
        user_shell = pwd.getpwuid(os.getuid()).pw_shell
    except Exception:
        user_shell = "/bin/sh"
    
    shell_command = f"{user_shell} -l -c {shlex.quote(command)}"

    # execute the user's command.
    executor = await create_subprocess_shell(
        shell_command,
        stdout=PIPE,
        stderr=PIPE,
        stdin=PIPE
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
