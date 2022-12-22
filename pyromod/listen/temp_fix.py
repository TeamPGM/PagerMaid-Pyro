import pyrogram
from pyrogram.enums.auto_name import AutoName
from pyrogram.errors import BadRequest, SessionPasswordNeeded
from pyrogram.types import User, TermsOfService, SentCode
from pyrogram.utils import ainput


async def temp_fix(
    client: "pyrogram.Client",
    message: pyrogram.raw.base.Message,
    users: dict,
    chats: dict,
    is_scheduled: bool = False,
    replies: int = 1
):
    parsed = await pyrogram.types.Message.old_parse(client, message, users, chats, is_scheduled, replies)  # noqa
    if isinstance(message, pyrogram.raw.types.Message) and message.reply_to \
            and hasattr(message.reply_to, "forum_topic") and message.reply_to.forum_topic \
            and not message.reply_to.reply_to_top_id:
        parsed.reply_to_top_message_id = parsed.reply_to_message_id
        parsed.reply_to_message_id = None
        parsed.reply_to_message = None
    return parsed


class NewSentCodeType(AutoName):
    """Sent code type enumeration used in :obj:`~pyrogram.types.SentCode`."""

    APP = pyrogram.raw.types.auth.SentCodeTypeApp
    "The code was sent through the telegram app."

    CALL = pyrogram.raw.types.auth.SentCodeTypeCall
    "The code will be sent via a phone call. A synthesized voice will tell the user which verification code to input."

    FLASH_CALL = pyrogram.raw.types.auth.SentCodeTypeFlashCall
    "The code will be sent via a flash phone call, that will be closed immediately."

    MISSED_CALL = pyrogram.raw.types.auth.SentCodeTypeMissedCall
    "Missed call."

    SMS = pyrogram.raw.types.auth.SentCodeTypeSms
    "The code was sent via SMS."

    FRAGMENT_SMS = pyrogram.raw.types.auth.SentCodeTypeFragmentSms
    "The code was sent via Fragment SMS."


class NewNextCodeType(AutoName):
    """Next code type enumeration used in :obj:`~pyrogram.types.SentCode`."""

    CALL = pyrogram.raw.types.auth.CodeTypeCall
    "The code will be sent via a phone call. A synthesized voice will tell the user which verification code to input."

    FLASH_CALL = pyrogram.raw.types.auth.CodeTypeFlashCall
    "The code will be sent via a flash phone call, that will be closed immediately."

    MISSED_CALL = pyrogram.raw.types.auth.CodeTypeMissedCall
    "Missed call."

    SMS = pyrogram.raw.types.auth.CodeTypeSms
    "The code was sent via SMS."

    FRAGMENT_SMS = pyrogram.raw.types.auth.SentCodeTypeFragmentSms
    "The code was sent via Fragment SMS."


def sent_code_parse(sent_code: pyrogram.raw.types.auth.SentCode):
    try:
        return SentCode.old_parse(sent_code)  # noqa
    except Exception:
        return SentCode(
            type=NewSentCodeType(type(sent_code.type)),  # noqa
            phone_code_hash=sent_code.phone_code_hash,
            next_type=NewNextCodeType(type(sent_code.next_type)) if sent_code.next_type else None,
            timeout=sent_code.timeout
        )


async def fix_authorize(self: "pyrogram.Client"):
    if self.bot_token:
        return await self.sign_in_bot(self.bot_token)

    print(f"Welcome to Pyrogram (version {pyrogram.__version__})")
    print(f"Pyrogram is free software and comes with ABSOLUTELY NO WARRANTY. Licensed\n"
          f"under the terms of the {pyrogram.__license__}.\n")

    while True:
        try:
            if not self.phone_number:
                while True:
                    value = await ainput("Enter phone number or bot token: ")

                    if not value:
                        continue

                    confirm = (await ainput(f'Is "{value}" correct? (y/N): ')).lower()

                    if confirm == "y":
                        break

                if ":" in value:
                    self.bot_token = value
                    return await self.sign_in_bot(value)
                else:
                    self.phone_number = value

            sent_code = await self.send_code(self.phone_number)
        except BadRequest as e:
            print(e.MESSAGE)
            self.phone_number = None
            self.bot_token = None
        else:
            break

    sent_code_descriptions = {
        pyrogram.enums.SentCodeType.APP: "Telegram app",
        pyrogram.enums.SentCodeType.SMS: "SMS",
        pyrogram.enums.SentCodeType.CALL: "phone call",
        pyrogram.enums.SentCodeType.FLASH_CALL: "phone flash call",
        NewSentCodeType.APP: "Telegram app",
        NewSentCodeType.SMS: "SMS",
        NewSentCodeType.CALL: "phone call",
        NewSentCodeType.FLASH_CALL: "phone flash call",
        NewSentCodeType.FRAGMENT_SMS: "fragment sms",
    }
    print(sent_code.type)
    print(sent_code.next_type)

    print(f"The confirmation code has been sent via {sent_code_descriptions[sent_code.type]}")

    while True:
        if not self.phone_code:
            self.phone_code = await ainput("Enter confirmation code: ")

        try:
            signed_in = await self.sign_in(self.phone_number, sent_code.phone_code_hash, self.phone_code)
        except BadRequest as e:
            print(e.MESSAGE)
            self.phone_code = None
        except SessionPasswordNeeded as e:
            print(e.MESSAGE)

            while True:
                print("Password hint: {}".format(await self.get_password_hint()))

                if not self.password:
                    self.password = await ainput("Enter password (empty to recover): ", hide=self.hide_password)

                try:
                    if not self.password:
                        confirm = await ainput("Confirm password recovery (y/n): ")

                        if confirm == "y":
                            email_pattern = await self.send_recovery_code()
                            print(f"The recovery code has been sent to {email_pattern}")

                            while True:
                                recovery_code = await ainput("Enter recovery code: ")

                                try:
                                    return await self.recover_password(recovery_code)
                                except BadRequest as e:
                                    print(e.MESSAGE)
                                except Exception as e:
                                    pyrogram.client.log.error(e, exc_info=True)
                                    raise
                        else:
                            self.password = None
                    else:
                        return await self.check_password(self.password)
                except BadRequest as e:
                    print(e.MESSAGE)
                    self.password = None
        else:
            break

    if isinstance(signed_in, User):
        return signed_in

    while True:
        first_name = await ainput("Enter first name: ")
        last_name = await ainput("Enter last name (empty to skip): ")

        try:
            signed_up = await self.sign_up(
                self.phone_number,
                sent_code.phone_code_hash,
                first_name,
                last_name
            )
        except BadRequest as e:
            print(e.MESSAGE)
        else:
            break

    if isinstance(signed_in, TermsOfService):
        print("\n" + signed_in.text + "\n")
        await self.accept_terms_of_service(signed_in.id)

    return signed_up
