import asyncio
from urllib.parse import urlparse

import aiopg
from pytube import YouTube
from telepot import glance
from telepot.aio import Bot
from telepot.aio.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

from secret import TELEGRAM_TOKEN, DSN


async def handle_message(msg):
    content_type, chat_type, chat_id = glance(msg)

    if content_type == 'text':
        handle_class = ProcessMessage(msg['text'], chat_id)
        if msg['text'].startswith('/look_videos'):
            print(msg['text'])
        else:
            await handle_class.start()


async def handle_callback(msg):
    query_id, from_id, query_data = glance(msg, flavor='callback_query')
    
    handle_class = ProcessMessage(query_data, from_id)
    await handle_class.start(force=True)


class ProcessMessage(object):

    def __init__(self, msg, chat_id):
        self.msg = msg
        self.chat_id = chat_id
        self.keyboard = None

    async def start(self, force=False):
        if self.check_message():
            async with aiopg.connect(DSN) as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute('SELECT id FROM videos WHERE url = (%s)', (self.msg,))
                    if await self.check_exist(cursor) or force:
                        message = await self.load_video(cursor, force)
                    else:
                        message = 'This video is exist!'
                        self.keyboard = InlineKeyboardMarkup(inline_keyboard=[
                            [InlineKeyboardButton(text='Скачать еще раз?', callback_data=self.msg)],
                        ])
        else:
            message = self.msg
        if not self.keyboard:
            self.keyboard = ReplyKeyboardMarkup(keyboard=[
                 [KeyboardButton(text='/look_videos')],
            ])
        await bot.sendMessage(self.chat_id, message, reply_markup=self.keyboard)

    async def load_video(self, cursor, force):
        try:
            video = self.fetch_video()
            if force:
                await cursor.execute('UPDATE videos SET download = false WHERE url = (%s)', (self.msg,))
            else:
                await cursor.execute('INSERT INTO videos(name, url) VALUES (%s, %s)', (video.filename, self.msg))
            return video.filename
        except Exception as e:
            return str(e)

    def check_message(self):
        return urlparse(self.msg).netloc in ('www.youtube.com', 'youtu.be')

    def fetch_video(self):
        yt = YouTube(self.msg)
        return yt.get('mp4', '720p')

    async def check_exist(self, cursor):
        await cursor.execute('SELECT id FROM videos WHERE url = (%s)', (self.msg,))
        return cursor.rowcount == 0


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.set_debug(True)
    bot = Bot(TELEGRAM_TOKEN)
    loop.create_task(MessageLoop(bot, {'chat': handle_message, 'callback_query': handle_callback}).run_forever())
    loop.run_forever()
