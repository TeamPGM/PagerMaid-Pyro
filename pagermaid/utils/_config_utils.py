from pagermaid.config import Config


def lang(text: str) -> str:
    """i18n"""
    return Config.lang_dict.get(text, Config.lang_default_dict.get(text, text))


def alias_command(command: str, disallow_alias: bool = False) -> str:
    """alias"""
    return command if disallow_alias else Config.alias_dict.get(command, command)
