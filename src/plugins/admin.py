from io import BytesIO
from sys import executable
from os import path, listdir, getcwd, execvp

from pyrogram import Client, filters
from pyrogram.errors import MessageTooLong

from src import allowed_users
from src.utils.readable import HumanFormat

@Client.on_message(filters.command(["ls", "log"]) & filters.user(allowed_users))
async def ls(_, message):
    if message.command[0].startswith("log"):
        return await message.reply_document("bot-log.txt", caption="`Bot Log`")
    args = message.text.split(None, 1)
    basepath = (
        f"{getcwd()}/{args[1]}{'' if args[1].endswith('/') else '/'}"
        if len(args) == 2
        else f"{getcwd()}/"
    )
    directory, listfile = "", ""
    try:
        file_list = sorted(listdir(basepath))
        for entry in file_list:
            fpath = path.join(basepath, entry)
            if path.isdir(fpath):
                size = HumanFormat.ToBytes(HumanFormat.PathSize(fpath))
                directory += f"\n📂 `{entry}` (`{size}`)"
            if path.isfile(fpath):
                size = HumanFormat.ToBytes(HumanFormat.PathSize(fpath))
                listfile += f"\n📄 `{entry}` (`{size}`)"
        text = f"**Path :** `{basepath}`\n\n**List Directory :**{directory}\n\n**List File :**{listfile}"
        return await message.reply_text(text, quote=True)
    except FileNotFoundError:
        return await message.reply_text("`File/Folder Not Found.`", quote=True)
    except MessageTooLong:
        with BytesIO(text.encode()) as file:
            file.name = "File-List.txt"
            return await message.reply_document(
                file, caption="File List Too Long.", quote=True
            )


@Client.on_message(filters.command("restart") & filters.user(allowed_users))
async def restart(_, m):
    await m.reply("Restart will done in few seconds.")
    execvp(executable, [executable, "-m", "src"])