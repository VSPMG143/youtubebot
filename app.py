import asyncio
import time
from urllib.parse import urlparse

import aiopg
from pytube import YouTube
from telepot import glance
from telepot.aio import Bot
from telepot.aio.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton

from secret import TELEGRAM_TOKEN, DSN


async def handle(msg):
    content_type, chat_type, chat_id = glance(msg)

    if content_type == 'text':
       await process_message(msg['text'], chat_id)


async def process_message(msg, chat_id):
    if urlparse(msg).netloc in ('www.youtube.com', 'youtu.be'):
        async with aiopg.connect(DSN) as conn:
            async with conn.cursor() as cursor:
                await cursor.execute('SELECT id FROM videos WHERE url = (%s)', (msg,))  
                if cursor.rowcount == 0:
                    try:
                        yt = YouTube(msg)
                        video = yt.get('mp4', '720p')
                        await cursor.execute("INSERT INTO videos(name, url) VALUES (%s, %s)", (video.filename, msg))
                        message = video.filename
                    except Exception as e:
                        message = str(e)
                else:
                    message = 'This video is exist!'
                    keyboard = InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text='Скачать еще раз?', callback_data=url)],
                    ])

    else:
    	message = msg
    await bot.sendMessage(chat_id, message)


async def handle_callback(msg):
    query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')

    await process_callback(query_data, from_id)


async def process_callback(msg, chat_id):
    if urlparse(msg).netloc in ('www.youtube.com', 'youtu.be'):
        async with aiopg.connect(DSN) as conn:
            async with conn.cursor() as cursor:
                try:
                    yt = YouTube(msg)
                    video = yt.get('mp4', '720p')
                    await cursor.execute('UPDATE videos SET download = false WHERE url = (%s)', (msg,))
                    message = video.filename
                except Exception as e:
                    message = str(e)
    else:
        message = msg
    await bot.sendMessage(chat_id, message)


loop = asyncio.get_event_loop()
loop.set_debug(True)
bot = Bot(TELEGRAM_TOKEN)
loop.create_task(MessageLoop(bot, 
    {'chat': handle},
    {'callback_query': handle_callback}
).run_forever())
loop.run_forever()

