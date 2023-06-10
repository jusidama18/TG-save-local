import uvloop
import pyromod

from os import getenv, path

from pyrogram import Client
from dotenv import load_dotenv

uvloop.install()

if path.exists("config.env"):
    load_dotenv("config.env", override=True)

api_id, api_hash = getenv("API_ID", default=6), getenv("API_HASH", default="eb06d4abfb49dc3eeb1aeb98ae0f581e")

session_string = getenv("SESSION_STRING", default=None)

userbot = Client("user", api_id=api_id, api_hash=api_hash, session_string=session_string, max_concurrent_transmissions=1000)

app = Client("bot", api_id=api_id, api_hash=api_hash, bot_token=getenv("BOT_TOKEN", default=None), max_concurrent_transmissions=1000, plugins=dict(root="src/plugins"))

if session_string is not None:
    app.userbot = userbot
    app.userbot.start()
else:
    app.userbot = None