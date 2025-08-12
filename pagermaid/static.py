from typing import Callable, Awaitable, Set, Dict

from datetime import datetime, timezone

from os import getcwd


working_dir = getcwd()
# solve same process
read_context = {}
help_messages = {}
hook_functions: Dict[str, Set[Callable[[], Awaitable[None]]]] = {
    "startup": set(),
    "shutdown": set(),
    "command_pre": set(),
    "command_post": set(),
    "process_error": set(),
    "load_plugins_finished": set(),
    "reload_pre": set(),
}
all_permissions = []
start_time = datetime.now(timezone.utc)
