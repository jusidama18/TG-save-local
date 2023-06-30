import logging
import aiofiles
import asyncio

from pathlib import Path

from datetime import datetime

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import ChatForwardsRestricted

from src import allowed_users
from src.utils.progress import Progress, ProgressTask
from src.utils.telegram import get_tg_link_content
from src.utils.readable import HumanFormat

logger = logging.getLogger(__name__)

logger.info("Bot Start")


async def filter_tg_link(client, text):
    should_del, is_single = False, False
    bot_id = client.me.username
    try:
        logger.info(f"Extract Media From URL : {text}")
        messages, session = await get_tg_link_content(text, client, client.userbot)
        check_single = text.split("?")
        if len(check_single) > 1 and check_single[1] == "single":
            is_single = True
    except ValueError as e:
        return (f"ValueError: {e}", should_del, is_single)

    if messages.chat.type.name not in ["SUPERGROUP", "CHANNEL"] and session != "user":
        return ("Use SuperGroup to download with User!", should_del, is_single)

    if session == "user":
        try:
            messages = await client.userbot.copy_message(
                chat_id=bot_id, from_chat_id=messages.chat.id, message_id=messages.id
            )
        except ChatForwardsRestricted:
            return (messages, should_del, is_single)
        should_del = True

    return (
        (messages, should_del, is_single)
        if messages.media
        else ("Link Provided not telegram media.", False, is_single)
    )


@Client.on_message(filters.command(["save", "remove"]) & filters.user(allowed_users))
async def save(client, message):
    target: str = message.command[0]
    if target.startswith("save") and message.chat.type.value != "private":
        if not message.reply_to_message:
            return await message.reply(
                "Reply To Supported Message Media or Text with TG Links", quote=True
            )
        return await download(client, message.reply_to_message)
    elif target.startswith("remove"):
        if len(message.command) > 1:
            if Path(message.command[1]).exists():
                await aiofiles.os.remove(message.command[1])
                status = "Success"
            else:
                status = "Failed"
            text = f"**{status} to delete :** `{message.command[1]}`"
        else:
            text = "**Provide path to remove.**"
        return await message.reply(text, quote=True)


@Client.on_message(filters.private & filters.user(allowed_users), group=1)
async def download(client, message):
    folder_name = None
    download_dir = Path("downloads")
    date = datetime.now().strftime("%Y-%m-%d %H:%M")
    start = datetime.now().timestamp()
    if message.media_group_id:
        messages = await message.get_media_group()
        folder_name = f"TG-MediaGroup [{messages[0].media.value}] [{date}]"
    elif message.media and not message.empty:
        if (file_ := message.document) and (file_.mime_type == "text/plain"):
            async with aiofiles.open(await message.download(), "r+") as f:
                links_list = [
                    line.strip() for line in await f.readlines() if len(line) != 0
                ]
            messages = [
                line
                for line in links_list
                if line.startswith(("https://t.me/", "tg://openmessage?user_id="))
            ]
        else:
            messages = [message]
    elif message.text:
        links_list = [
            item.strip() for item in message.text.splitlines() if len(item) != 0
        ]
        messages = [
            line
            for line in links_list
            if line.startswith(("https://t.me/", "tg://openmessage?user_id="))
        ]
    else:
        return await message.reply("`Send File or Telegram message of file link`")

    if messages:
        msg = await message.reply(f"`Start Download {len(messages)} Files`")
        if len(messages) > 1 and not folder_name:
            folder_name = f"TG-BatchDL [{date}]"

        if folder_name:
            download_dir = download_dir.joinpath(folder_name)

        success, num = [], 1
        for index, file in enumerate(messages, start=1):
            file_delete, temp_folder = False, None

            if isinstance(file, dict):
                temp_folder = file["folder"]
                file = file["file"]
            elif not isinstance(file, Message):
                o_file = file
                file, file_delete, is_single = await filter_tg_link(client, file)
                if len(messages) > 1 and isinstance(file, str):
                    await msg.reply(f"{o_file} > `{file}`", quote=True)
                    continue

                if file.media_group_id and not is_single:
                    more_file = await file.get_media_group()
                    file = more_file[0]
                    while True:
                        temp_folder = f"TG-MediaGroup #{num} [{file.media.value}]"
                        if not download_dir.joinpath(temp_folder).is_dir():
                            break
                        num += 1
                    __data = [{"folder": temp_folder, "file": i}
                              for i in more_file[1:]]
                    messages.extend(__data)

            if not file.empty and file.media:
                file_data = getattr(file, file.media.value, None)
                file_name = getattr(file_data, "file_name", None)

                new_folder_dir = download_dir
                if not folder_name and temp_folder or folder_name and temp_folder:
                    new_folder_dir = new_folder_dir.joinpath(temp_folder)
                elif not folder_name:
                    new_folder_dir = new_folder_dir.joinpath(
                        str(file.media.value).title()
                    ).joinpath(str(date).split()[0])
                if file_name:
                    new_folder_dir = new_folder_dir.joinpath(
                        file_name).absolute()
                    if new_folder_dir.exists():
                        new_folder_dir.unlink()
                else:
                    new_folder_dir = f"{new_folder_dir.absolute()}/"

                prog = Progress(
                    message=msg,
                    user=message.from_user.id,
                    client=client,
                    chatID=message.chat.id,
                    mID=message.id,
                    prog_text="`Downloading This File!`",
                    file_name=new_folder_dir,
                    extra_text=({"Files": f"{index} / {len(messages)}"}),
                )

                logger.info(f"Start Downloading : {new_folder_dir}")
                output = await file.download(new_folder_dir, progress=prog.progress)
                if output is not None:
                    success.append(output)
                await asyncio.sleep(0.5)

                if file_delete:
                    await file.delete()

        if success:
            dlTime = HumanFormat.Time(datetime.now().timestamp() - start)
            footer = f"\n\n**Time Taken : {dlTime}**"
            folder_size = HumanFormat.ToBytes(
                sum(HumanFormat.PathSize(f) for f in success)
            )
            header = f"**Finish Download [{len(success)}/{len(messages)}] [{folder_size}] :**\n"
            body = ""
            for index, output in enumerate(success, start=1):
                body += f"\n**{index}.** `{output}` **[{HumanFormat.ToBytes(HumanFormat.PathSize(output))}]**"
                if len(body) > 4000:
                    message = await message.reply(header + body + footer, quote=True)
                    body = ""
            if body != "":
                message = await message.reply(header + body + footer, quote=True)
            await msg.delete()


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
