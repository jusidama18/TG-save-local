#!/usr/bin/env python3

import re

from aiofiles import open as aiopen
from aiofiles.os import remove
from pyrogram import Client


async def get_links_from_message(text, bulk_start: int = None, bulk_end: int = None):
    if not bulk_start:
        bulk_start = 0
    if not bulk_end:
        bulk_end = 0

    links_list = text.split("\n")
    links_list = [item.strip() for item in links_list if len(item) != 0]

    if bulk_start != 0 and bulk_end != 0:
        links_list = links_list[bulk_start:bulk_end]
    elif bulk_start != 0:
        links_list = links_list[bulk_start:]
    elif bulk_end != 0:
        links_list = links_list[:bulk_end]

    return links_list


async def get_links_from_file(message, bulk_start: int = None, bulk_end: int = None):
    if not bulk_start:
        bulk_start = 0
    if not bulk_end:
        bulk_end = 0

    links_list = []
    text_file_dir = await message.download()

    async with aiopen(text_file_dir, "r+") as f:
        lines = await f.readlines()
        links_list.extend(line.strip() for line in lines if len(line) != 0)

    if bulk_start != 0 and bulk_end != 0:
        links_list = links_list[bulk_start:bulk_end]
    elif bulk_start != 0:
        links_list = links_list[bulk_start:]
    elif bulk_end != 0:
        links_list = links_list[:bulk_end]

    await remove(text_file_dir)

    return links_list


async def extract_bulk_links(message, bulk_start: int = None, bulk_end: int = None):
    if not bulk_start:
        bulk_start = 0
    if not bulk_end:
        bulk_end = 0

    if (
        (reply_to := message.reply_to_message)
        and (file_ := reply_to.document)
        and (file_.mime_type == "text/plain")
    ):
        return await get_links_from_file(message.reply_to_message, bulk_start, bulk_end)
    elif text := message.reply_to_message.text:
        return await get_links_from_message(text, bulk_start, bulk_end)
    return []


async def get_tg_link_content(link, bot: Client, user: Client = None):
    message = None
    if link.startswith("https://t.me/"):
        private = False
        msg = re.match(r"https:\/\/t\.me\/(?:c\/)?([^\/]+)\/([0-9]+)", link)
    else:
        private = True
        msg = re.match(
            r"tg:\/\/openmessage\?user_id=([0-9]+)&message_id=([0-9]+)", link
        )
        if not user:
            raise ValueError("SESSION_STRING required for this private link!")

    chat = msg[1]
    msg_id = int(msg[2])
    if chat.isdigit():
        chat = int(chat) if private else int(f"-100{chat}")

    if not private:
        try:
            message = await bot.get_messages(chat_id=chat, message_ids=msg_id)
            if message.empty:
                private = True
        except Exception as e:
            private = True
            if not user:
                raise e

    if private and user:
        try:
            user_message = await user.get_messages(chat_id=chat, message_ids=msg_id)
        except Exception as e:
            raise ValueError(
                f"You don't have access to this chat!. ERROR: {e}") from e
        if not user_message.empty:
            return user_message, "user"
        else:
            raise ValueError("Private: Please report!")
    elif not private:
        return message, "bot"
    else:
        raise ValueError("Bot can't download from GROUPS without joining!")
