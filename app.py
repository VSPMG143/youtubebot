import argparse
import asyncio
from urllib.parse import urlparse

import aiopg
from pytube import YouTube, Playlist
from telepot import glance
from telepot.aio import Bot
from telepot.aio.api import set_proxy
from telepot.aio.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

from secret import TELEGRAM_TOKEN, DSN
from utils import get_stream


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
    
    path, msg = query_data.split(ProcessMessage.DIVIDER)
    handle_class = ProcessMessage(msg, from_id)
    await getattr(handle_class, path).start(force=True)


class ProcessMessage(object):
    DIVIDER = '$#@'
    ONE_MORE = 'reload'

    def __init__(self, msg, chat_id):
        self.msg = msg
        self.chat_id = chat_id
        self.keyboard = None
        self.videos = []

    async def start(self, force=False):
        if self.check_message():
            async with aiopg.connect(DSN) as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute('SELECT id FROM videos WHERE url = (%s)', (self.msg,))
                    if await self.check_exist(cursor) or force:
                        videos = self.get_videos()
                        message = ''
                        for video in videos:
                            message += await self.load_video(cursor, video, force)
                    else:
                        message = 'This video is exist!'
                        callback_data = f'{self.ONE_MORE}{self.DIVIDER}{self.msg}'
                        self.keyboard = InlineKeyboardMarkup(inline_keyboard=[
                            [InlineKeyboardButton(text='Скачать еще раз?', callback_data=callback_data)],
                        ])
        else:
            message = self.msg
        if not self.keyboard:
            self.keyboard = ReplyKeyboardMarkup(keyboard=[
                 [KeyboardButton(text='/look_videos')],
            ])
        await bot.sendMessage(self.chat_id, message, reply_markup=self.keyboard)

    def get_videos(self):
        try:
            playlist = Playlist(self.msg)
            playlist.populate_video_urls()
            videos = playlist.video_urls
        except IndexError:
            videos = [self.msg]
        return videos

    async def load_video(self, cursor, video, force):
        try:
            stream = self.fetch_stream(video)
            if force:
                await cursor.execute('UPDATE videos SET download = false WHERE url = (%s)', (video,))
            else:
                await cursor.execute(
                    'INSERT INTO videos(name, url) VALUES (%s, %s)', (stream.default_filename, video)
                )
            return stream.default_filename
        except Exception as e:
            return str(e)

    def check_message(self):
        return urlparse(self.msg).netloc in ('www.youtube.com', 'youtu.be')

    @staticmethod
    def fetch_stream(video):
        yt = YouTube(video)
        return get_stream(yt)

    async def check_exist(self, cursor):
        await cursor.execute('SELECT id FROM videos WHERE url = (%s)', (self.msg,))
        return cursor.rowcount == 0

    async def reload(self):
        async with aiopg.connect(DSN) as conn:
            async with conn.cursor() as cursor:
                videos = self.get_videos()
                message = ''
                for video in videos:
                    message += await self.load_video(cursor, video, True)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.set_debug(True)
    bot = Bot(TELEGRAM_TOKEN)
    parser = argparse.ArgumentParser()
    parser.add_argument('--proxy', type=str, help='proxy ip')
    args = parser.parse_args()
    if args.proxy:
        set_proxy(args.proxy)
    loop.create_task(MessageLoop(bot, {'chat': handle_message, 'callback_query': handle_callback}).run_forever())
    loop.run_forever()
