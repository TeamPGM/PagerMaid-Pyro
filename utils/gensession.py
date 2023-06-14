import asyncio
import contextlib
import os
from sys import executable, exit

try:
    from pyrogram.errors import ApiIdInvalid, PhoneNumberInvalid
    from pyrogram import Client

    print("Found an existing installation of Pyrogram...\nSuccessfully Imported.")
except ImportError:
    print("Installing Pyrogram...")
    os.system(f"{executable} -m pip install pyrogram")
    print("Done. Installed and imported pyrogram.")
    from pyrogram.errors import ApiIdInvalid, PhoneNumberInvalid
    from pyrogram import Client


async def main():
    API_ID = 0
    try:
        API_ID = int(input("Please enter your API ID: "))
    except ValueError:
        print("APP ID must be an integer.\nQuitting...")
        exit(0)
    except Exception as e:
        raise e

    API_HASH = input("Please enter your API HASH: ")
    try:
        async with Client("pagermaid", API_ID, API_HASH) as bot:
            print("Generating a user session...")
            await bot.send_message(
                "me",
                f"**PagerMaid** `String SESSION`:\n\n`{await bot.export_session_string()}`",
            )
            print(
                "Your SESSION has been generated. Check your telegram saved messages!"
            )
            exit(0)
    except ApiIdInvalid:
        print(
            "Your API ID/API HASH combination is invalid. Kindly recheck.\nQuitting..."
        )
        exit(0)
    except ValueError:
        print("API HASH must not be empty!\nQuitting...")
        exit(0)
    except PhoneNumberInvalid:
        print("The phone number is invalid!\nQuitting...")
        exit(0)


if __name__ == "__main__":
    with contextlib.closing(asyncio.new_event_loop()) as loop:
        loop.run_until_complete(main())
