import uvloop
import logging

from os import getenv, path

from pyrogram import Client
from dotenv import load_dotenv

uvloop.install()

if path.exists("config.env"):
    load_dotenv("config.env", override=True)

logging.basicConfig(
    format="%(asctime)s - %(name)s [%(levelname)s] : %(message)s",
    handlers=[
        logging.FileHandler("bot-log.txt", mode="w"),
        logging.StreamHandler(),
    ],
    level=logging.INFO,
    datefmt="%d/%b/%Y | %I:%M:%S %p",
)

logging.getLogger("pyrogram").setLevel(logging.WARNING)

api_id, api_hash = (
    int(getenv("API_ID") or 6),
    getenv("API_HASH") or "eb06d4abfb49dc3eeb1aeb98ae0f581e",
)

session_string = getenv("SESSION_STRING") or None

userbot = Client(
    "user",
    api_id=api_id,
    api_hash=api_hash,
    session_string=session_string,
    sleep_threshold=10,
    max_concurrent_transmissions=1000,
)
bot_token = getenv("BOT_TOKEN") or None

if not bot_token:
    logging.error("Add 'BOT_TOKEN', exit now.")
    exit(1)

app = Client(
    "bot",
    api_id=api_id,
    api_hash=api_hash,
    bot_token=bot_token,
    max_concurrent_transmissions=1000,
    sleep_threshold=10,
    plugins=dict(root="src/plugins"),
)

if session_string is not None:
    app.userbot = userbot
    app.userbot.start()
else:
    app.userbot = None

allowed_users = list(map(int, str(getenv("ALLOWED_USERS", "")).split()))

if app.userbot:
    allowed_users.append(app.userbot.me.id)