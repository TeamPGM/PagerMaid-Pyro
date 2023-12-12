import asyncio
import base64
from typing import Optional

import pyrogram
from pyqrcode import QRCode
from pyrogram import Client
from pyrogram.errors import SessionPasswordNeeded, BadRequest
from pyrogram.session import Auth, Session
from pyrogram.utils import ainput

from pagermaid import Config
from pyromod.utils.errors import QRCodeWebNeedPWDError, QRCodeWebCodeError


async def sign_in_qrcode(
    client: Client,
) -> Optional[str]:
    req = await client.invoke(
        pyrogram.raw.functions.auth.ExportLoginToken(
            api_id=client.api_id,
            api_hash=client.api_hash,
            except_ids=[],
        )
    )

    if isinstance(req, pyrogram.raw.types.auth.LoginToken):
        token = base64.b64encode(req.token)
        return f"tg://login?token={token.decode('utf-8')}"
    elif isinstance(req, pyrogram.raw.types.auth.LoginTokenMigrateTo):
        await client.session.stop()
        await client.storage.dc_id(req.dc_id)
        await client.storage.auth_key(
            await Auth(
                client, await client.storage.dc_id(), await client.storage.test_mode()
            ).create()
        )
        client.session = Session(
            client,
            await client.storage.dc_id(),
            await client.storage.auth_key(),
            await client.storage.test_mode(),
        )
        await client.session.start()
        req = await client.invoke(
            pyrogram.raw.functions.auth.ImportLoginToken(token=req.token)
        )
        await client.storage.user_id(req.authorization.user.id)
        await client.storage.is_bot(False)
        return pyrogram.types.User._parse(client, req.authorization.user)
    elif isinstance(req, pyrogram.raw.types.auth.LoginTokenSuccess):
        await client.storage.user_id(req.authorization.user.id)
        await client.storage.is_bot(False)
        return pyrogram.types.User._parse(client, req.authorization.user)


async def authorize_by_qrcode(
    client: Client,
):
    print(f"Welcome to Pyrogram (version {pyrogram.__version__})")
    print(
        f"Pyrogram is free software and comes with ABSOLUTELY NO WARRANTY. Licensed\n"
        f"under the terms of the {pyrogram.__license__}.\n"
    )

    while True:
        qrcode = None
        try:
            qrcode = await sign_in_qrcode(client)
        except BadRequest as e:
            print(e.MESSAGE)
        except SessionPasswordNeeded as e:
            print(e.MESSAGE)
            while True:
                print(f"Password hint: {await client.get_password_hint()}")

                if not client.password:
                    client.password = await ainput(
                        "Enter password (empty to recover): ", hide=client.hide_password
                    )

                try:
                    if client.password:
                        return await client.check_password(client.password)
                    confirm = await ainput("Confirm password recovery (y/n): ")

                    if confirm == "y":
                        email_pattern = await client.send_recovery_code()
                        print(f"The recovery code has been sent to {email_pattern}")

                        while True:
                            recovery_code = await ainput("Enter recovery code: ")

                            try:
                                return await client.recover_password(recovery_code)
                            except BadRequest as e:
                                print(e.MESSAGE)
                    else:
                        client.password = None
                except BadRequest as e:
                    print(e.MESSAGE)
                    client.password = None
        if isinstance(qrcode, str):
            qr_obj = QRCode(qrcode)
            try:
                qr_obj.png("data/qrcode.png", scale=6)
            except Exception:
                print("Save qrcode.png failed.")
            print(qr_obj.terminal())
            print(
                f"Scan the QR code above, the qrcode.png file or visit {qrcode} to log in.\n"
            )
            print(
                "QR code will expire in 20 seconds. If you have scanned it, please wait..."
            )
            await asyncio.sleep(20)
        elif isinstance(qrcode, pyrogram.types.User):
            return qrcode


async def authorize_by_qrcode_web(
    client: Client,
    password: Optional[str] = None,
):
    qrcode = None
    try:
        if password:
            client.password = password
            raise SessionPasswordNeeded()
        qrcode = await sign_in_qrcode(client)
    except BadRequest as e:
        raise e
    except SessionPasswordNeeded as e:
        try:
            if client.password:
                return await client.check_password(client.password)
        except BadRequest as e:
            client.password = None
            raise e
        raise QRCodeWebNeedPWDError(await client.get_password_hint()) from e
    if isinstance(qrcode, str):
        raise QRCodeWebCodeError(qrcode)
    elif isinstance(qrcode, pyrogram.types.User):
        return qrcode


async def start_client(client: Client):
    is_authorized = await client.connect()

    try:
        if not is_authorized:
            if Config.QRCODE_LOGIN:
                await authorize_by_qrcode(client)
            else:
                await client.authorize()

        if not await client.storage.is_bot() and client.takeout:
            client.takeout_id = (
                await client.invoke(pyrogram.raw.functions.account.InitTakeoutSession())
            ).id

        await client.invoke(pyrogram.raw.functions.updates.GetState())
    except (Exception, KeyboardInterrupt):
        await client.disconnect()
        raise
    else:
        client.me = await client.get_me()
        await client.initialize()

        return client
