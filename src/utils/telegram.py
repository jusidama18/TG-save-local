#!/usr/bin/env python3

import re

from pyrogram import Client


async def get_tg_link_content(link, bot: Client, user: Client = None):
    message = None
    if link.startswith("https://t.me/"):
        private = False
        msg = re.match(
            r"https:\/\/t\.me\/(?:c\/)?([^\/]+)(?:\/[^\/]+)?\/([0-9]+)", link
        )
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
        raise ValueError("Private: Please report!")
    if not private:
        return message, "bot"
    else:
        raise ValueError("Bot can't download from GROUPS without joining!")
