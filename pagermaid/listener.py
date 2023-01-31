import asyncio
import contextlib
import sys
from time import strftime, gmtime, time
from traceback import format_exc

from pyrogram import ContinuePropagation, StopPropagation, filters, Client
from pyrogram.errors import Flood, Forbidden
from pyrogram.errors.exceptions.bad_request_400 import (
    MessageIdInvalid,
    MessageNotModified,
    MessageEmpty,
    UserNotParticipant, PeerIdInvalid
)
from pyrogram.handlers import MessageHandler, EditedMessageHandler

from pagermaid import help_messages, logs, Config, bot, read_context, all_permissions
from pagermaid.common.ignore import ignore_groups_manager
from pagermaid.group_manager import Permission
from pagermaid.inject import inject
from pagermaid.single_utils import Message, AlreadyInConversationError, TimeoutConversationError, ListenerCanceled
from pagermaid.utils import lang, attach_report, sudo_filter, alias_command, get_permission_name, process_exit
from pagermaid.hook import Hook

_lock = asyncio.Lock()


def listener(**args):
    """ Register an event listener. """
    command = args.get("command")
    disallow_alias = args.get("disallow_alias", False)
    need_admin = args.get("need_admin", False)
    description = args.get("description")
    parameters = args.get("parameters")
    pattern = sudo_pattern = args.get("pattern")
    diagnostics = args.get("diagnostics", True)
    ignore_edited = args.get("ignore_edited", False)
    is_plugin = args.get("is_plugin", True)
    incoming = args.get("incoming", False)
    outgoing = args.get("outgoing", True)
    groups_only = args.get("groups_only", False)
    privates_only = args.get("privates_only", False)
    priority = args.get("priority", 50)
    block_process = args.get("block_process", False)

    if priority < 0 or priority > 100:
        raise ValueError("Priority must be between 0 and 100.")
    elif priority == 0 and is_plugin:
        """ Priority 0 is reserved for modules. """
        priority = 1
    elif (not is_plugin) and need_admin:
        priority = 0

    if command is not None:
        if command in help_messages:
            if help_messages[alias_command(command)]["priority"] <= priority:
                raise ValueError(f"{lang('error_prefix')} {lang('command')} \"{command}\" {lang('has_reg')}")
            else:
                block_process = True
        pattern = fr"^(,|，){alias_command(command, disallow_alias)}(?: |$)([\s\S]*)"
        sudo_pattern = fr"^(/){alias_command(command, disallow_alias)}(?: |$)([\s\S]*)"
    if pattern is not None and not pattern.startswith("(?i)"):
        args["pattern"] = f"(?i){pattern}"
    else:
        args["pattern"] = pattern
    if sudo_pattern is not None and not sudo_pattern.startswith("(?i)"):
        sudo_pattern = f"(?i){sudo_pattern}"
    if outgoing and not incoming:
        base_filters = filters.me & ~filters.via_bot & ~filters.forwarded
    elif incoming and not outgoing:
        base_filters = filters.incoming & ~filters.me
    else:
        base_filters = filters.all
    permission_name = get_permission_name(is_plugin, need_admin, command)
    sudo_filters = (
            sudo_filter(permission_name)
            & ~filters.via_bot
            & ~filters.forwarded
    )
    if args["pattern"]:
        base_filters &= filters.regex(args["pattern"])
        sudo_filters &= filters.regex(sudo_pattern)
    if groups_only:
        base_filters &= filters.group
        sudo_filters &= filters.group
    if privates_only:
        base_filters &= filters.private
        sudo_filters &= filters.private
    if "ignore_edited" in args:
        del args["ignore_edited"]
    if "command" in args:
        del args["command"]
    if "diagnostics" in args:
        del args["diagnostics"]
    if "description" in args:
        del args["description"]
    if "parameters" in args:
        del args["parameters"]
    if "is_plugin" in args:
        del args["is_plugin"]
    if "owners_only" in args:
        del args["owners_only"]
    if "admins_only" in args:
        del args["admins_only"]
    if "groups_only" in args:
        del args["groups_only"]
    if "need_admin" in args:
        del args["need_admin"]
    if "priority" in args:
        del args["priority"]
    if "block_process" in args:
        del args["block_process"]

    def decorator(function):

        async def handler(client: Client, message: Message):
            try:
                # ignore
                try:
                    if ignore_groups_manager.check_id(message.chat.id):
                        raise ContinuePropagation
                except ContinuePropagation:
                    raise ContinuePropagation
                except BaseException:
                    pass
                try:
                    parameter = message.matches[0].group(2).split(" ")
                    if parameter == [""]:
                        parameter = []
                    message.parameter = parameter
                    message.arguments = message.matches[0].group(2)
                except BaseException:
                    message.parameter = None
                    message.arguments = None
                # solve same process
                async with _lock:
                    if (message.chat.id, message.id) in read_context:
                        raise ContinuePropagation
                    read_context[(message.chat.id, message.id)] = True

                if command:
                    await Hook.command_pre(message, command)
                if data := inject(message, function):
                    await function(**data)
                else:
                    if function.__code__.co_argcount == 0:
                        await function()
                    if function.__code__.co_argcount == 1:
                        await function(message)
                    elif function.__code__.co_argcount == 2:
                        await function(client, message)
                if command:
                    await Hook.command_post(message, command)
            except StopPropagation as e:
                raise StopPropagation from e
            except KeyboardInterrupt as e:
                raise KeyboardInterrupt from e
            except (UserNotParticipant, MessageNotModified, MessageEmpty, Flood, Forbidden, PeerIdInvalid):
                logs.warning(
                    "An unknown chat error occurred while processing a command.",
                )
            except MessageIdInvalid:
                logs.warning(
                    "Please Don't Delete Commands While it's Processing.."
                )
            except AlreadyInConversationError:
                logs.warning(
                    "Please Don't Send Commands In The Same Conversation.."
                )
                with contextlib.suppress(BaseException):
                    await message.edit(lang("conversation_already_in_error"))
            except TimeoutConversationError:
                logs.warning(
                    "Conversation Timed out while processing commands.."
                )
                with contextlib.suppress(BaseException):
                    await message.edit(lang("conversation_timed_out_error"))
            except ListenerCanceled:
                logs.warning(
                    "Listener Canceled While Processing Commands.."
                )
                with contextlib.suppress(BaseException):
                    await message.edit(lang("reload_des"))
            except ContinuePropagation as e:
                if block_process:
                    raise StopPropagation from e
                raise ContinuePropagation from e
            except SystemExit:
                await process_exit(start=False, _client=client, message=message)
                await Hook.shutdown()
                sys.exit(0)
            except BaseException:
                exc_info = sys.exc_info()[1]
                exc_format = format_exc()
                with contextlib.suppress(BaseException):
                    await message.edit(lang("run_error"), no_reply=True)  # noqa
                if not diagnostics:
                    return
                if Config.ERROR_REPORT:
                    report = f"""# Generated: {strftime('%H:%M %d/%m/%Y', gmtime())}. \n# ChatID: {message.chat.id}. \n# UserID: {message.from_user.id if message.from_user else message.sender_chat.id}. \n# Message: \n-----BEGIN TARGET MESSAGE-----\n{message.text or message.caption}\n-----END TARGET MESSAGE-----\n# Traceback: \n-----BEGIN TRACEBACK-----\n{str(exc_format)}\n-----END TRACEBACK-----\n# Error: "{str(exc_info)}". \n"""

                    await attach_report(report, f"exception.{time()}.pgp.txt", None,
                                        "PGP Error report generated.")
                    await Hook.process_error_exec(message, command, exc_info, exc_format)
            if (message.chat.id, message.id) in read_context:
                del read_context[(message.chat.id, message.id)]
            if block_process:
                message.stop_propagation()
            message.continue_propagation()

        bot.add_handler(MessageHandler(handler, filters=base_filters), group=0 + priority)
        if command:
            bot.add_handler(MessageHandler(handler, filters=sudo_filters), group=50 + priority)
        if not ignore_edited:
            bot.add_handler(EditedMessageHandler(handler, filters=base_filters), group=1 + priority)
            if command:
                bot.add_handler(EditedMessageHandler(handler, filters=sudo_filters), group=51 + priority)

        return handler

    if description is not None and command is not None:
        if parameters is None:
            parameters = ""
        help_messages.update({
            f"{alias_command(command)}": {"permission": permission_name,
                                          "use": f"**{lang('use_method')}:** `,{command} {parameters}`\n"
                                                 f"**{lang('need_permission')}:** `{permission_name}`\n"
                                                 f"{description}",
                                          "priority": priority, }
        })
        all_permissions.append(Permission(permission_name))

    return decorator


def raw_listener(filter_s):
    """Simple Decorator To Handel Custom Filters"""

    def decorator(function):
        async def handler(client, message):
            # ignore
            try:
                if ignore_groups_manager.check_id(message.chat.id):
                    raise ContinuePropagation
            except ContinuePropagation:
                raise ContinuePropagation
            except BaseException:
                pass
            # solve same process
            async with _lock:
                if (message.chat.id, message.id) in read_context:
                    raise ContinuePropagation
                read_context[(message.chat.id, message.id)] = True
            try:
                if function.__code__.co_argcount == 1:
                    await function(message)
                elif function.__code__.co_argcount == 2:
                    await function(client, message)
            except StopPropagation as e:
                raise StopPropagation from e
            except ContinuePropagation as e:
                raise ContinuePropagation from e
            except MessageIdInvalid:
                logs.warning(
                    "Please Don't Delete Commands While it's Processing.."
                )
            except AlreadyInConversationError:
                logs.warning(
                    "Please Don't Send Commands In The Same Conversation.."
                )
                with contextlib.suppress(BaseException):
                    await message.edit(lang("conversation_already_in_error"))
            except TimeoutConversationError:
                logs.warning(
                    "Conversation Timed out while processing commands.."
                )
                with contextlib.suppress(BaseException):
                    await message.edit(lang("conversation_timed_out_error"))
            except ListenerCanceled:
                logs.warning(
                    "Listener Canceled While Processing Commands.."
                )
                with contextlib.suppress(BaseException):
                    await message.edit(lang("reload_des"))
            except SystemExit:
                await process_exit(start=False, _client=client, message=message)
                await Hook.shutdown()
                sys.exit(0)
            except (UserNotParticipant, MessageNotModified, MessageEmpty, Flood, Forbidden):
                pass
            except BaseException:
                exc_info = sys.exc_info()[1]
                exc_format = format_exc()
                with contextlib.suppress(BaseException):
                    await message.edit(lang('run_error'), no_reply=True)
                if Config.ERROR_REPORT:
                    report = f"# Generated: {strftime('%H:%M %d/%m/%Y', gmtime())}. \n" \
                             f"# ChatID: {message.chat.id}. \n" \
                             f"# UserID: {message.from_user.id if message.from_user else message.sender_chat.id}. \n" \
                             f"# Message: \n-----BEGIN TARGET MESSAGE-----\n" \
                             f"{message.text}\n-----END TARGET MESSAGE-----\n" \
                             f"# Traceback: \n-----BEGIN TRACEBACK-----\n" \
                             f"{str(exc_format)}\n-----END TRACEBACK-----\n" \
                             f"# Error: \"{str(exc_info)}\". \n"
                    await attach_report(report, f"exception.{time()}.pagermaid", None,
                                        "Error report generated.")
            message.continue_propagation()

        bot.add_handler(MessageHandler(handler, filters=filter_s), group=2)

        return handler

    return decorator
