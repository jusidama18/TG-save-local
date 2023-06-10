from pyrogram import Client, filters

from src.utils.progress import Progress, ProgressTask
from src.utils.telegram import get_tg_link_content  # , extract_bulk_links


@Client.on_message(filters.private)
async def download(client, message):
    if message.media_group_id:
        messages = await message.get_media_group()
        msg = await message.reply(f"`Start Download {len(messages)} Files`")
        prog = Progress(
            message=msg,
            user=message.from_user.id,
            client=client,
            chatID=message.chat.id,
            mID=message.id,
            prog_text="`Downloading This File!`",
        )
        text = "**Finish Download :**\n"
        for index, file in enumerate(messages, start=1):
            if not file.empty:
                file_data = getattr(file, file.media.value, None)
                prog.file_name = (getattr(file_data, "file_name", None),)
                prog.extra_text = ({"Files": f"{index} / {len(messages)}"},)
                output = await file.download(progress=prog.progress)
                text += f"**{index}.** `{output}`"
        await msg.edit(text)
    elif message.media and not messages.empty:
        msg = await message.reply("`Start Download File`")
        prog = Progress(
            message=msg,
            user=message.from_user.id,
            client=client,
            chatID=message.chat.id,
            mID=message.id,
            prog_text="`Downloading This File!`",
        )
        file_data = getattr(file, file.media.value, None)
        prog.file_name = (getattr(file_data, "file_name", None),)
        output = await file.download(progress=prog.progress)
        await msg.edit(f"**Finish Download :** `{output}`")
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
            prog = Progress(
                message=msg,
                user=message.from_user.id,
                client=client,
                chatID=message.chat.id,
                mID=message.id,
                prog_text="`Downloading This File!`",
            )
            file_data = getattr(messages, messages.media.value, None)
            prog.file_name = (getattr(file_data, "file_name", None),)
            await messages.download(progress=prog.progress)
        else:
            await message.reply("Download what?")


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
            "This Is Not Your Download. So, dont touch on this...😡😡", show_alert=True
        )
