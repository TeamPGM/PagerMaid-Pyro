import asyncio
import sys
from typing import TYPE_CHECKING

from pyrogram import StopPropagation

from pagermaid.inject import inject
from pagermaid.static import hook_functions
from pagermaid.utils import logs

if TYPE_CHECKING:
    from pagermaid.enums import Message


class Hook:
    @staticmethod
    def on_startup():
        """
        注册一个启动钩子
        """

        def decorator(function):
            hook_functions["startup"].add(function)
            return function

        return decorator

    @staticmethod
    def on_shutdown():
        """
        注册一个关闭钩子
        """

        def decorator(function):
            hook_functions["shutdown"].add(function)
            return function

        return decorator

    @staticmethod
    def command_preprocessor():
        """
        注册一个命令预处理钩子
        """

        def decorator(function):
            hook_functions["command_pre"].add(function)
            return function

        return decorator

    @staticmethod
    def command_postprocessor():
        """
        注册一个命令后处理钩子
        """

        def decorator(function):
            hook_functions["command_post"].add(function)
            return function

        return decorator

    @staticmethod
    def process_error():
        """
        注册一个错误处理钩子
        """

        def decorator(function):
            hook_functions["process_error"].add(function)
            return function

        return decorator

    @staticmethod
    def load_success():
        """
        注册一个插件加载完成钩子
        """

        def decorator(function):
            hook_functions["load_plugins_finished"].add(function)
            return function

        return decorator

    @staticmethod
    async def startup():
        if cors := [
            startup(**inject(None, startup)) for startup in hook_functions["startup"]
        ]:  # noqa
            try:
                await asyncio.gather(*cors)
            except Exception as exception:
                logs.info(f"[startup]: {type(exception)}: {exception}")

    @staticmethod
    async def shutdown():
        if cors := [
            shutdown(**inject(None, shutdown))
            for shutdown in hook_functions["shutdown"]
        ]:  # noqa
            try:
                await asyncio.gather(*cors)
            except Exception as exception:
                logs.info(f"[shutdown]: {type(exception)}: {exception}")

    @staticmethod
    async def command_pre(message: "Message", command, sub_command):
        cors = []
        try:
            for pre in hook_functions["command_pre"]:
                try:
                    data = inject(
                        message, pre, command=command, sub_command=sub_command
                    )
                except Exception as exception:
                    logs.info(f"[process_error]: {type(exception)}: {exception}")
                    continue
                cors.append(pre(**data))  # noqa
            if cors:
                await asyncio.gather(*cors)
        except SystemExit:
            await Hook.shutdown()
            sys.exit(0)
        except StopPropagation as e:
            raise StopPropagation from e
        except Exception as exception:
            logs.info(f"[command_pre]: {type(exception)}: {exception}")

    @staticmethod
    async def command_post(message: "Message", command, sub_command):
        cors = []
        try:
            for post in hook_functions["command_post"]:
                try:
                    data = inject(
                        message, post, command=command, sub_command=sub_command
                    )
                except Exception as exception:
                    logs.info(f"[process_error]: {type(exception)}: {exception}")
                    continue
                cors.append(post(**data))  # noqa
            if cors:
                await asyncio.gather(*cors)
        except SystemExit:
            await Hook.shutdown()
            sys.exit(0)
        except StopPropagation as e:
            raise StopPropagation from e
        except Exception as exception:
            logs.info(f"[command_post]: {type(exception)}: {exception}")

    @staticmethod
    async def process_error_exec(
        message: "Message", command, exc_info: BaseException, exc_format: str
    ):
        cors = []
        try:
            for error in hook_functions["process_error"]:
                try:
                    data = inject(
                        message,
                        error,
                        command=command,
                        exc_info=exc_info,
                        exc_format=exc_format,
                    )
                except Exception as exception:
                    logs.info(f"[process_error]: {type(exception)}: {exception}")
                    continue
                cors.append(error(**data))  # noqa
            if cors:
                await asyncio.gather(*cors)
        except SystemExit:
            await Hook.shutdown()
            sys.exit(0)
        except StopPropagation as e:
            raise StopPropagation from e
        except Exception as exception:
            logs.info(f"[process_error]: {type(exception)}: {exception}")

    @staticmethod
    async def load_success_exec():
        if cors := [
            load(**inject(None, load))
            for load in hook_functions["load_plugins_finished"]
        ]:  # noqa
            try:
                await asyncio.gather(*cors)
            except Exception as exception:
                logs.info(f"[load_success_exec]: {type(exception)}: {exception}")
