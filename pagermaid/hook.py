import asyncio

from pagermaid import startup_functions, shutdown_functions, logs


class Hook:
    @staticmethod
    def on_startup():
        """
        注册一个启动钩子
        """
        def decorator(function):
            startup_functions.add(function)
            return function
        return decorator

    @staticmethod
    def on_shutdown():
        """
        注册一个关闭钩子
        """
        def decorator(function):
            shutdown_functions.add(function)
            return function
        return decorator

    @staticmethod
    async def startup():
        if cors := [startup() for startup in startup_functions]:
            try:
                await asyncio.gather(*cors)
            except Exception as exception:
                logs.info(f"[startup]: {type(exception)}: {exception}")

    @staticmethod
    async def shutdown():
        if cors := [shutdown() for shutdown in shutdown_functions]:
            try:
                await asyncio.gather(*cors)
            except Exception as exception:
                logs.info(f"[shutdown]: {type(exception)}: {exception}")
