import contextlib
from os import remove


def safe_remove(name: str) -> None:
    with contextlib.suppress(FileNotFoundError):
        remove(name)
