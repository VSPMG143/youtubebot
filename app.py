import asyncio
import time
from urllib.parse import urlparse

import aiosqlite
from pytube import YouTube
from telepot import glance
from telepot.aio import Bot
from telepot.aio.loop import MessageLoop

from settings import DB_NAME
from secret import TELEGRAM_TOKEN


async def handle(msg):
    content_type, chat_type, chat_id = glance(msg)

    if content_type == 'text':
       await process_message(msg['text'], chat_id)


async def process_message(msg, chat_id):
    if urlparse(msg).netloc == 'www.youtube.com':
        async with aiosqlite.connect(DB_NAME) as db:
            cursor = await db.execute("SELECT id FROM videos WHERE url = ?", (msg,))
            if cursor.rowcount == -1:
                try:
                    yt = YouTube(msg)
                    video = yt.get('mp4', '720p')
                    await db.execute("INSERT INTO videos(name, url) VALUES (?,?)", (video.filename, msg))
                    await db.commit()
                    message = video.filename
                except Exception as e:
                    message = str(e)
            else:
                message = "This video is exist!"
    else:
    	message = msg
    await bot.sendMessage(chat_id, message)


# logging.basicConfig(format=LOG_FORMAT, level=LOG_LEVEL , filename=LOG_FILENAME)


loop = asyncio.get_event_loop()
loop.set_debug(True)
bot = Bot(TELEGRAM_TOKEN)
loop.create_task(MessageLoop(bot, handle).run_forever())
loop.run_forever()

