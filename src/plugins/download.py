import os
from datetime import datetime
from io import BytesIO
from pyrogram import Client, filters, errors

from src.utils.progress import Progress, ProgressTask
from src.utils.telegram import get_tg_link_content  # , extract_bulk_links
from src.utils.readable import HumanFormat


@Client.on_message(filters.private, group=1)
async def download(client, message):
    start = datetime.now()
    if message.media_group_id:
        messages = await message.get_media_group()
        msg = await message.reply(f"`Start Download {len(messages)} Files`")
        text = "**Finish Download :**\n"
        for index, file in enumerate(messages, start=1):
            if not file.empty:
                file_data = getattr(file, file.media.value, None)
                file_name = (getattr(file_data, "file_name", None),)
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
                output = await file.download(progress=prog.progress)
                text += f"\n**{index}.** `{output}` **[{HumanFormat.ToBytes(os.stat(output).st_size)}]**"
        dlTime = HumanFormat.Time(datetime.now().timestamp() - start)
        text += f"\n\n**Time Taken : {dlTime}**"
        await msg.edit(text)
    elif message.media and not message.empty:
        msg = await message.reply("`Start Download File`")
        file_data = getattr(message, message.media.value, None)
        file_name = (getattr(file_data, "file_name", None),)
        prog = Progress(
            message=msg,
            user=message.from_user.id,
            client=client,
            chatID=message.chat.id,
            mID=message.id,
            prog_text="`Downloading This File!`",
            file_name=file_name,
        )

        output = await message.download(progress=prog.progress)
        dlTime = HumanFormat.Time(datetime.now().timestamp() - start)
        if prog.is_cancelled:
            if os.path.exists(output):
                os.remove(output)
            return await msg.edit(
                f"**Download [** `{file_name}` **] is cancelled in** `{dlTime}`"
            )

        await msg.edit(
            f"**Finish Download in {dlTime} :** `{output}` **[{HumanFormat.ToBytes(os.stat(output).st_size)}]**"
        )
    elif message.text.startswith(("https://t.me/", "tg://openmessage?user_id=")):
        msg = await message.reply("`Start Download File`")
        try:
            messages, session = await get_tg_link_content(
                message.text, client, client.userbot
            )
        except ValueError as e:
            return await msg.edit(e)

        if client.userbot.me.is_premium and session != "bot" or session == "user":
            if (
                messages.chat.type.name not in ["SUPERGROUP", "CHANNEL"]
                and session != "user"
            ):
                return await message.reply("Use SuperGroup to download with User!")

            messages = await client.userbot.get_messages(
                chat_id=messages.chat.id, message_ids=messages.id
            )
            messages = await messages.copy(client.me.id)
        if messages.media and not messages.empty:
            file_data = getattr(messages, messages.media.value, None)
            file_name = (getattr(file_data, "file_name", None),)
            prog = Progress(
                message=msg,
                user=message.from_user.id,
                client=client,
                chatID=message.chat.id,
                mID=message.id,
                prog_text="`Downloading This File!`",
                file_name=file_name,
            )

            output = await messages.download(progress=prog.progress)
            dlTime = HumanFormat.Time(datetime.now().timestamp() - start)
            if prog.is_cancelled:
                if os.path.exists(output):
                    os.remove(output)
                return await msg.edit(
                    f"**Download [** `{file_name}` **] is cancelled in** `{dlTime}`"
                )

            await msg.edit(
                f"**Finish Download in {dlTime} :** `{output}` **[{HumanFormat.ToBytes(os.stat(output).st_size)}]**"
            )
        else:
            await message.reply("Download what?")
    else:
        return await message.reply("`Send File or Telegram message of file link`")


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


@Client.on_message(filters.command("ls"))
async def ls(_, message):
    args = message.text.split(None, 1)
    basepath = (
        f"{os.getcwd()}/{args[1]}{'' if args[1].endswith('/') else '/'}"
        if len(args) == 2
        else f"{os.getcwd()}/"
    )
    directory, listfile = "", ""
    try:
        file_list = os.listdir(basepath)
        file_list.sort()
        for entry in file_list:
            path = os.path.join(basepath, entry)
            if os.path.isdir(path):
                size = HumanFormat.ToBytes(HumanFormat.PathSize(path))
                directory += f"\n📂 `{entry}` (`{size}`)"
            if os.path.isfile(path):
                size = HumanFormat.ToBytes(os.stat(path).st_size)
                listfile += f"\n📄 `{entry}` (`{size}`)"
        text = f"**Path :** `{basepath}`\n\n**List Directory :**{directory}\n\n**List File :**{listfile}"
        return await message.reply_text(text, quote=True)
    except FileNotFoundError:
        return await message.reply_text("`File/Folder Not Found.`", quote=True)
    except errors.MessageTooLong:
        with BytesIO(text.encode()) as file:
            file.name = "File-List.txt"
            return await message.reply_document(
                file, caption="File List Too Long.", quote=True
            )
