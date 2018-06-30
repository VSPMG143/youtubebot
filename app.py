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
    
    path, msg = query_data.split(BaseProcessMessage.DIVIDER)
    if path == BaseProcessMessage.ONE_MORE:
        handle_class = ProcessMessageReload(msg, from_id)
    elif path == BaseProcessMessage.LOAD_LIST:
        handle_class = ProcessMessageList(msg, from_id)
    elif path == BaseProcessMessage.LOAD_ONE:
        handle_class = ProcessMessageOne(msg, from_id)
    else:
        return
    await handle_class.start()


class BaseProcessMessage(object):
    DIVIDER = '$#@'
    ONE_MORE = 'reload'
    LOAD_LIST = 'list'
    LOAD_ONE = 'one'

    def __init__(self, msg, chat_id):
        self.msg = msg
        self.chat_id = chat_id
        self.keyboard = None
        self.videos = []

    def check_message(self):
        return urlparse(self.msg).netloc in ('www.youtube.com', 'youtu.be')

    def get_videos(self):
        try:
            playlist = Playlist(self.msg)
            playlist.populate_video_urls()
            videos = playlist.video_urls
        except IndexError:
            videos = [self.msg]
        return videos

    def get_stream(self, yt):
        streams = yt.streams.filter(file_extension='mp4', type='video').order_by('resolution').desc().all()
        for stream in streams:
            if stream.includes_audio_track and stream.resolution <= '720p':
                return stream
        return yt.streams.first()

    async def start(self):
        if self.check_message():
            await self.process_message()
        else:
            message = self.msg
            await bot.sendMessage(self.chat_id, message, reply_markup=self.keyboard)

    async def process_message(self):
        pass

    async def send_message(self, message):
        await bot.sendMessage(self.chat_id, message, reply_markup=self.keyboard)

    async def load_video(self, cursor, video):
        try:
            stream = self.fetch_stream(video)
            await cursor.execute(
                'INSERT INTO videos(name, url) VALUES (%s, %s)', (stream.default_filename, video)
            )
            return stream.default_filename
        except Exception as e:
            return str(e)

    @staticmethod
    def fetch_stream(video):
        yt = YouTube(video)
        return get_stream(yt)

    async def check_exist(self, cursor):
        await cursor.execute('SELECT id FROM videos WHERE url = (%s)', (self.msg,))
        return cursor.rowcount == 0


class ProcessMessage(BaseProcessMessage):

    async def process_message(self):
        async with aiopg.connect(DSN) as conn:
            async with conn.cursor() as cursor:
                await cursor.execute('SELECT id FROM videos WHERE url = (%s)', (self.msg,))
                if await self.check_exist(cursor):
                    videos = self.get_videos()
                    if isinstance(videos, list):
                        message = 'Will you want load playlist?'
                        callback_data = f'{self.LOAD_LIST}{self.DIVIDER}{self.msg}'
                        callback_data2 = f'{self.LOAD_ONE}{self.DIVIDER}{self.msg}'
                        self.keyboard = InlineKeyboardMarkup(inline_keyboard=[
                            [InlineKeyboardButton(text='Скачать весь плэйлист?', callback_data=callback_data)],
                            [InlineKeyboardButton(text='Скачать только это видео?', callback_data=callback_data2)]
                        ])
                    else:
                        message = await self.load_video(cursor, videos)
                else:
                    message = 'This video is exist!'
                    callback_data = f'{self.ONE_MORE}{self.DIVIDER}{self.msg}'
                    self.keyboard = InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text='Скачать еще раз?', callback_data=callback_data)],
                    ])
                await self.send_message(message)


class ProcessMessageReload(BaseProcessMessage):

    async def process_message(self):
        async with aiopg.connect(DSN) as conn:
            async with conn.cursor() as cursor:
                message = await self.load_video(cursor, self.msg)
                await self.send_message(message)

    async def load_video(self, cursor, video,):
        try:
            stream = self.fetch_stream(video)
            await cursor.execute('UPDATE videos SET download = false WHERE url = (%s)', (video,))
            return stream.default_filename
        except Exception as e:
            return str(e)


class ProcessMessageList(BaseProcessMessage):
    async def process_message(self):
        async with aiopg.connect(DSN) as conn:
            async with conn.cursor() as cursor:
                videos = self.get_videos()
                for video in videos:
                    message = await self.load_video(cursor, video)
                    await self.send_message(message)


class ProcessMessageOne(BaseProcessMessage):
    async def process_message(self):
        async with aiopg.connect(DSN) as conn:
            async with conn.cursor() as cursor:
                message = await self.load_video(cursor, self.msg)
                await self.send_message(message)


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
