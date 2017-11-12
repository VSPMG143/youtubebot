import asyncio
import time
from urllib.parse import urlparse

from pytube import YouTube
from telepot import glance
from telepot.aio import Bot
from telepot.aio.loop import MessageLoop

from secret import TELEGRAM_TOKEN
from db import check_url, insert_row


async def handle(msg):
    content_type, chat_type, chat_id = glance(msg)

    if content_type == 'text':
       await process_message(msg['text'], chat_id)


async def process_message(msg, chat_id):
    if urlparse(msg).netloc == 'www.youtube.com' and check_url(msg):
        try:
            yt = YouTube(msg)
            video = yt.get('mp4', '720p')
            insert_row((video.filename, msg))
            message = video.filename
        except Exception as e:
            message = str(e)
    else:
    	message = msg
    await bot.sendMessage(chat_id, message)


# logging.basicConfig(format=LOG_FORMAT, level=LOG_LEVEL , filename=LOG_FILENAME)


loop = asyncio.get_event_loop()
loop.set_debug(True)
bot = Bot(TELEGRAM_TOKEN)
loop.create_task(MessageLoop(bot, handle).run_forever())
loop.run_forever()

