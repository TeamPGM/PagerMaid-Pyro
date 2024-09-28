import contextlib
from os import remove

from pyrogram.errors import UsernameNotOccupied, PeerIdInvalid
from pyrogram.types import User

from pagermaid.config import Config
from pagermaid.enums import Message, Client
from pagermaid.listener import listener
from pagermaid.utils import lang


@listener(
    is_plugin=False,
    command="profile",
    description=lang("profile_des"),
    parameters="<username>",
)
async def profile(client: Client, message: Message):
    """Queries profile of a user."""
    if len(message.parameter) > 1:
        await message.edit(f"{lang('error_prefix')}{lang('arg_error')}")
        return
    if not Config.SILENT:
        message = await message.edit(lang("profile_process"))
    if message.reply_to_message:
        user = message.reply_to_message.from_user
        if not user:
            return await message.edit(f"{lang('error_prefix')}{lang('profile_e_no')}")
    else:
        if len(message.parameter) == 1:
            user = message.parameter[0]
            if user.isdigit():
                user = int(user)
        else:
            user = await client.get_me()
        if message.entities is not None:
            if message.entities[0].type == "text_mention":
                user = message.entities[0].user
            elif message.entities[0].type == "phone_number":
                user = int(message.parameter[0])
            else:
                return await message.edit(f"{lang('error_prefix')}{lang('arg_error')}")
        if not isinstance(user, User):
            try:
                user = await client.get_users(user)
            except PeerIdInvalid:
                return await message.edit(
                    f"{lang('error_prefix')}{lang('profile_e_nof')}"
                )
            except UsernameNotOccupied:
                return await message.edit(
                    f"{lang('error_prefix')}{lang('profile_e_nou')}"
                )
            except OverflowError:
                return await message.edit(
                    f"{lang('error_prefix')}{lang('profile_e_long')}"
                )
            except Exception as exception:
                raise exception
    user_type = "Bot" if user.is_bot else lang("profile_user")
    username_system = (
        f"@{user.username}" if user.username is not None else lang("profile_noset")
    )
    if not user.first_name:
        await message.edit(f"{lang('error_prefix')}{lang('profile_e_no')}")
        return
    first_name = user.first_name.replace("\u2060", "")
    last_name = (
        user.last_name.replace("\u2060", "")
        if user.last_name is not None
        else lang("profile_noset")
    )
    verified = lang("profile_yes") if user.is_verified else lang("profile_no")
    restricted = lang("profile_yes") if user.is_restricted else lang("profile_no")
    caption = (
        f"**{lang('profile_name')}:** \n"
        f"{lang('profile_username')}: {username_system} \n"
        f"ID: {user.id} \n"
        f"{lang('profile_fname')}: {first_name} \n"
        f"{lang('profile_lname')}: {last_name} \n"
        f"{lang('profile_verified')}: {verified} \n"
        f"{lang('profile_restricted')}: {restricted} \n"
        f"{lang('profile_type')}: {user_type} \n"
        f"[{first_name}](tg://user?id={user.id})"
    )
    photo = await client.download_media(user.photo.big_file_id) if user.photo else None
    reply_to = message.reply_to_message.id if message.reply_to_message else None
    if photo:
        try:
            await client.send_photo(
                message.chat.id, photo, caption=caption, reply_to_message_id=reply_to
            )
            await message.delete()
            return remove(photo)
        except TypeError:
            await message.edit(caption)
    else:
        await message.edit(caption)


@listener(
    is_plugin=False,
    outgoing=True,
    command="block",
    need_admin=True,
    description=lang("block_des"),
    parameters="(username/uid/reply)",
)
async def block_user(client: Client, message: Message):
    """Block a user."""
    if len(message.parameter) > 1:
        await message.edit(f"{lang('error_prefix')}{lang('arg_error')}")
        return
    if not Config.SILENT:
        message = await message.edit(lang("block_process"))
    user = message.obtain_user()
    if not user:
        return await message.edit(f"{lang('error_prefix')}{lang('arg_error')}")
    with contextlib.suppress(Exception):
        if await client.block_user(user):
            return await message.edit(f"{lang('block_success')} `{user}`")
    await message.edit(f"`{user}` {lang('block_exist')}")


@listener(
    is_plugin=False,
    outgoing=True,
    command="unblock",
    need_admin=True,
    description=lang("unblock_des"),
    parameters="<username/uid/reply>",
)
async def unblock_user(client: Client, message: Message):
    """Unblock a user."""
    if len(message.parameter) > 1:
        await message.edit(f"{lang('error_prefix')}{lang('arg_error')}")
        return
    if not Config.SILENT:
        message = await message.edit(lang("unblock_process"))
    user = message.obtain_user()
    if not user:
        return await message.edit(f"{lang('error_prefix')}{lang('arg_error')}")
    with contextlib.suppress(Exception):
        if await client.unblock_user(user):
            return await message.edit(f"{lang('unblock_success')} `{user}`")
    await message.edit(f"`{user}` {lang('unblock_exist')}")
