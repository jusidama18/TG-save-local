import contextlib
import math

from datetime import datetime
from asyncio import sleep

from typing import List, Dict
from collections import defaultdict

from pyrogram import Client
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from pyrogram.errors import MessageNotModified, MessageIdInvalid

from src.utils.readable import HumanFormat

ProgressTask: Dict[int, List] = defaultdict(lambda: [])


class Progress:
    def __init__(
        self,
        message: Message,
        user: int,
        client: Client = None,
        chatID: int = None,
        mID: int = None,
        prog_text: str = None,
        file_name: str = None,
        extra_text: dict = None,
        sleep_time: int = None,
        wait: int = None,
    ) -> None:
        self._cancelled: bool = False
        self.wait: int = wait or 15

        self.message: Message = message
        self.client: Client = client or self.message._client

        self.user: int = user
        self.chatID: int = chatID or self.message.chat.id
        self.mID: int = mID or self.message.id

        self.start: int = datetime.now().timestamp()
        self.extra_text: dict = extra_text
        self.sleep_time = sleep_time
        self.prog_text: str = prog_text
        self.file_name: str = file_name

    @property
    def is_cancelled(self):
        task = ProgressTask[self.chatID]
        if task and self.mID in task:
            self._cancelled = True
        return self._cancelled

    async def progress(self, current, total):
        now = datetime.now().timestamp()
        reply_markup = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Cancel 🚫",
                        callback_data=f"progress {self.chatID} {self.mID} {self.user}",
                    )
                ]
            ]
        )

        if self.is_cancelled:
            await self.message.edit(
                f"😔 Cancelled/ERROR: `{self.prog_text}` ({HumanFormat.ToBytes(total)})"
            )
            await self._client.stop_transmission()
            _index = ProgressTask[self.chatID].index(self.mID)
            ProgressTask[self.chatID].pop(_index)


        diff = now - self.start
        caption = f"`{'=' * 50}`\n{self.prog_text}\n\n"
        if round(diff % float(self.wait)) == 0 or current == total:
            speed = current / diff
            elapsed_time = round(diff)
            time_to_completion = round((total - current) / speed)
            estimated_total_time = elapsed_time + time_to_completion
            percentage = current * 100 / total
            caption += "`[ {0}{1} ] {2}%`\n\n".format(
                "".join(["▓" for _ in range(math.floor(percentage / 5))]),
                "".join(["░" for _ in range(20 - math.floor(percentage / 5))]),
                round(percentage, 2),
            )
            if self.extra_text is not None and isinstance(self.extra_text, dict):
                caption += (
                    "\n".join(
                        f"**{key} :** `{value}`"
                        for key, value in self.extra_text.items()
                    )
                    + "\n"
                )
            caption += "**Size :** `{0} / {1}`\n**ETA :** `{2}`\n".format(
                HumanFormat.ToBytes(current),
                HumanFormat.ToBytes(total),
                HumanFormat.Time(estimated_total_time)
                if estimated_total_time != ""
                else "0 s",
            )
            caption += f"**Elapsed :** `{HumanFormat.Time(round(datetime.now().timestamp()) - round(self.start))}`\n"
            if self.file_name:
                caption += f"**File Name:** `{self.file_name}`\n"
            caption += f"**Speed :** `{HumanFormat.ToBytes((total - current) / (datetime.now().timestamp() - self.start))}/s`"
            caption += f"\n`{'=' * 50}`"
            with contextlib.suppress(MessageNotModified, MessageIdInvalid):
                self.message = await self.message.edit(
                    caption, reply_markup=reply_markup
                )
            if self.sleep_time:
                await sleep(self.sleep_time)
