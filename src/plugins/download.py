import logging
import aiofiles

from io import BytesIO
from aiofiles.os import remove, path, stat, listdir, getcwd

from datetime import datetime

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import MessageTooLong

from src import OWNER_ID
from src.utils.progress import Progress, ProgressTask
from src.utils.telegram import get_tg_link_content  # , extract_bulk_links
from src.utils.readable import HumanFormat

logger = logging.getLogger(__name__)

async def filter_tg_link(client, message):
    try:
        messages, session = await get_tg_link_content(
            message.text, client, client.userbot
        )
    except ValueError as e:
        return e

    if client.userbot.me.is_premium and session != "bot" or session == "user":
        if (
            messages.chat.type.name not in ["SUPERGROUP", "CHANNEL"]
            and session != "user"
        ):
            return "Use SuperGroup to download with User!"

        messages = await client.userbot.get_messages(
            chat_id=messages.chat.id, message_ids=messages.id
        )
        messages = await messages.copy(client.me.id)
    else:
        return "Download what?"


@Client.on_message(filters.private & filters.user(OWNER_ID), group=1)
async def download(client, message):
    start = datetime.now().timestamp()
    if message.media_group_id:
        messages = await message.get_media_group()
    elif message.media and not message.empty:
        if (file_ := message.document) and (file_.mime_type == "text/plain"):
            links_list = []
            text_file_dir = await message.download()
            async with aiofiles.open(text_file_dir, "r+") as f:
                lines = await f.readlines()
                links_list.extend(line.strip() for line in lines if len(line) != 0)
            messages = [line for line in links_list if line.startswith(("https://t.me/", "tg://openmessage?user_id="))]
        else:
            messages = [message]
    elif message.text.startswith(("https://t.me/", "tg://openmessage?user_id=")):
        messages = await filter_tg_link(client, message)
        if not isinstance(messages, Message):
            return await msg.edit(messages)
        messages = [messages]
    else:
        return await message.reply("`Send File or Telegram message of file link`")

    msg = await message.reply(f"`Start Download {len(messages)} Files`")
    text = "**Finish Download :**\n"
    allFinish = []
    for index, file in enumerate(messages, start=1):
        if not isinstance(file, Message):
            o_file = file
            file = await filter_tg_link(client, message)
            if len(messages) > 1 and isinstance(file, str):
                await msg.reply(f"{o_file} > `{file}`", quote=True)
                continue
        if file.media and not file.empty:
            file_data = getattr(file, file.media.value, None)
            file_name = getattr(file_data, "file_name", None)
            prog = Progress(
                message=msg,
                user=message.from_user.id,
                client=client,
                chatID=message.chat.id,
                mID=message.id,
                prog_text="`Downloading This File!`",
                file_name=file_name,
                extra_text=({"Files": f"{index} / {len(messages)}"}),
            )
            logger.info(f"Start Downloading : {file_name}")
            output = await file.download(progress=prog.progress)
            allFinish.append(output)
            if prog.is_cancelled:
                for fl in allFinish:
                    if await path.exists(fl):
                        await remove(fl)
                text = f"**All Download is cancelled in** `{dlTime}`\n"
                text += "\n".join(
                    f"{index}. {name}"
                    for index, name in enumerate(allFinish, start=1)
                )
                return await msg.edit(text)
            text += f"\n**{index}.** `{output}` **[{HumanFormat.ToBytes((await stat(path)).st_size)}]**"
    dlTime = HumanFormat.Time(datetime.now().timestamp() - start)
    text += f"\n\n**Time Taken : {dlTime}**"
    await msg.edit(text)

@Client.on_callback_query(
    filters.regex(r"^progress (?P<chatID>-?\d+) (?P<mID>\d+) (?P<user>\d+)")
)
async def cancel_download(_, query):
    if query.matches:
        data = query.matches[0]
    else:
        return await query.answer("Error regex.")
    if query.from_user.id == int(data["user"]):
        ProgressTask[int(data["chatID"])].append(int(data["mID"]))
        await query.answer("Trying to cancel...", show_alert=True)
    else:
        await query.answer(
            "This Is Not Your Download. So, dont touch on this.", show_alert=True
        )


@Client.on_message(filters.command("ls") & filters.user(OWNER_ID))
async def ls(_, message):
    args = message.text.split(None, 1)
    basepath = (
        f"{await getcwd()}/{args[1]}{'' if args[1].endswith('/') else '/'}"
        if len(args) == 2
        else f"{await getcwd()}/"
    )
    directory, listfile = "", ""
    try:
        file_list = await listdir(basepath)
        file_list.sort()
        for entry in file_list:
            path = await path.join(basepath, entry)
            if await path.isdir(path):
                size = HumanFormat.ToBytes(HumanFormat.PathSize(path))
                directory += f"\n📂 `{entry}` (`{size}`)"
            if await path.isfile(path):
                size = HumanFormat.ToBytes((await stat(path)).st_size)
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
