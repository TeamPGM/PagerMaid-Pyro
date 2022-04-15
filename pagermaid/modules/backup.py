""" Pagermaid backup and recovery plugin. """
import os
import tarfile
from traceback import format_exc

from pyrogram import Client

from pagermaid.config import Config
from pagermaid.listener import listener
from pagermaid.utils import upload_attachment, lang, Message

pgm_backup_zip_name = "pagermaid_backup.tar.gz"


def make_tar_gz(output_filename, source_dirs: list):
    """
    压缩 tar.gz 文件
    :param output_filename: 压缩文件名
    :param source_dirs: 需要压缩的文件列表
    :return: None
    """
    with tarfile.open(output_filename, "w:gz") as tar:
        for i in source_dirs:
            tar.add(i, arcname=os.path.basename(i))


def un_tar_gz(filename, dirs):
    """
    解压 tar.gz 文件
    :param filename: 压缩文件名
    :param dirs: 解压后的存放路径
    :return: bool
    """
    try:
        t = tarfile.open(filename, "r:gz")
        t.extractall(path=dirs)
        return True
    except Exception as e:
        print(e, format_exc())
        return False


@listener(is_plugin=False, outgoing=True, command="backup",
          description=lang('back_des'))
async def backup(_: Client, message: Message):
    await message.edit(lang('backup_process'))

    # Remove old backup
    if os.path.exists(pgm_backup_zip_name):
        os.remove(pgm_backup_zip_name)

    # remove mp3 , they are so big !
    for i in os.listdir("data"):
        if i.find(".mp3") != -1 or i.find(".jpg") != -1 or i.find(".flac") != -1 or i.find(".ogg") != -1:
            os.remove(f"data{os.sep}{i}")

    # run backup function
    make_tar_gz(pgm_backup_zip_name, ["data", "plugins", "config.yml"])
    if Config.LOG:
        await upload_attachment(pgm_backup_zip_name, Config.LOG_ID, None)
        await message.edit(lang("backup_success_channel"))
    else:
        await message.edit(lang("backup_success"))


@listener(is_plugin=False, outgoing=True, command="recovery",
          description=lang('recovery_des'))
async def recovery(_: Client, message: Message):
    reply = message.reply_to_message

    if reply.document:  # Overwrite local backup
        try:
            if ".tar.gz" in reply.document.file_name:  # Verify filename
                await message.edit(lang('recovery_down'))
                # Start download process
                pgm_backup_zip_name = await reply.download()  # noqa
            else:
                return await message.edit(lang('recovery_file_error'))
        except Exception as e:  # noqa
            print(e, format_exc())
            return await message.edit(lang('recovery_file_error'))
    else:
        return await message.edit(lang('recovery_file_error'))

    # Extract backup files
    await message.edit(lang('recovery_process'))
    if not os.path.exists(pgm_backup_zip_name):
        return await message.edit(lang('recovery_file_not_found'))
    elif not un_tar_gz(pgm_backup_zip_name, ""):
        os.remove(pgm_backup_zip_name)
        return await message.edit(lang('recovery_file_error'))

    # Cleanup
    if os.path.exists(pgm_backup_zip_name):
        os.remove(pgm_backup_zip_name)

    await message.edit(lang('recovery_success') + " " + lang('apt_reboot'))
    exit(1)
