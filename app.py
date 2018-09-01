import argparse
import asyncio
import logging.config
from abc import abstractmethod
from urllib.parse import urlparse

from aiopg.sa import create_engine
from pytube import YouTube, Playlist, Stream
from telepot import glance
from telepot.aio import Bot
from telepot.aio.api import set_proxy
from telepot.aio.loop import MessageLoop
from telepot.exception import TelegramError
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

from db import videos
from secret import *
from settings import LOGGING


logging.config.dictConfig(LOGGING)
logger = logging.getLogger('youtubebot')


async def handle_message(msg: dict):
    content_type, chat_type, chat_id = glance(msg)

    if content_type == 'text':
        logger.debug('Message data: %s', msg['text'])
        handle_class = ProcessMessage(msg['text'], chat_id)
        if msg['text'].startswith('/look_videos'):
            print(msg['text'])
        else:
            await handle_class.start()


async def handle_callback(msg: dict):
    query_id, from_id, query_data = glance(msg, flavor='callback_query')
    logger.debug('Callback data: %s', query_data)
    
    path, msg = query_data.split(BaseProcessMessage.DIVIDER)
    if path == BaseProcessMessage.ONE_MORE:
        handle_class = ProcessMessageReload(msg, from_id)
    elif path == BaseProcessMessage.LOAD_LIST:
        handle_class = ProcessMessageList(msg, from_id)
    elif path == BaseProcessMessage.LOAD_ONE:
        handle_class = ProcessMessageOne(msg, from_id)
    else:
        logger.error('Error. %s - path do not exist!', path)
        return
    await handle_class.start()


class BaseProcessMessage:
    DIVIDER = '$#@'
    ONE_MORE = 'reload'
    LOAD_LIST = 'list'
    LOAD_ONE = 'one'

    def __init__(self, msg, chat_id):
        self.msg = msg
        self.chat_id = chat_id
        self.keyboard = None
        self.videos = []
        self.engine = None
        self.retry = 5

    async def connect_db(self):
        self.engine = await create_engine(
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            loop=asyncio.get_event_loop()
        )

    def check_message(self) -> bool:
        return urlparse(self.msg).netloc in ('www.youtube.com', 'youtu.be')

    async def get_videos(self) -> list:
        return await asyncio.get_event_loop().run_in_executor(None, self._get_videos)

    def _get_videos(self) -> list:
        try:
            playlist = Playlist(self.msg)
            playlist.populate_video_urls()
            video_urls = playlist.video_urls
        except IndexError:
            video_urls = []
        logger.debug('Videos: %s', videos)
        return video_urls

    async def start(self):
        await self.connect_db()
        if self.check_message():
            await self.process_message()
        else:
            message = self.msg
            await self.send_message(message)

    @classmethod
    @abstractmethod
    async def process_message(cls):
        pass

    async def send_message(self, message: str) -> None:
        for i in range(self.retry):
            try:
                await bot.sendMessage(self.chat_id, message, reply_markup=self.keyboard)
                return 
            except TelegramError:
                logger.info(f'TelegramError, attempt number: {i}')
                asyncio.sleep(1)
        logger.error('final TelegramError')

    async def load_video(self, video: str) -> str:
        try:
            stream = await self.fetch_stream(video)
            query = videos.insert().values(
                name=stream.default_filename, url=video
            )
            async with self.engine.acquire() as connection:
                await connection.execute(query)
            return stream.default_filename
        except Exception as e:
            logger.error(str(e))
            return str(e)

    async def fetch_stream(self, video: str) -> Stream:
        return await asyncio.get_event_loop().run_in_executor(None, self._fetch_stream, video)

    @staticmethod
    def _fetch_stream(video: str) -> Stream:
        yt = YouTube(video)
        streams = yt.streams.filter(file_extension='mp4', type='video').order_by('resolution').desc().all()
        for stream in streams:
            if stream.includes_audio_track and stream.resolution <= '720p':
                return stream
        return yt.streams.first()

    async def check_exist(self) -> bool:
        query = videos.select().where(videos.c.url == self.msg)
        async with self.engine.acquire() as connection:
            res = await connection.execute(query)
            return bool(await res.fetchone())


class ProcessMessage(BaseProcessMessage):

    async def process_message(self):
        if not await self.check_exist():
            video_urls = await self.get_videos()
            if video_urls:
                message = 'Will you want load playlist?'
                callback_data = f'{self.LOAD_LIST}{self.DIVIDER}{self.msg}'
                callback_data2 = f'{self.LOAD_ONE}{self.DIVIDER}{self.msg}'
                self.keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text='Скачать весь плэйлист?', callback_data=callback_data)],
                    [InlineKeyboardButton(text='Скачать только это видео?', callback_data=callback_data2)]
                ])
            else:
                message = await self.load_video(self.msg)
        else:
            message = 'This video is exist!'
            callback_data = f'{self.ONE_MORE}{self.DIVIDER}{self.msg}'
            self.keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='Скачать еще раз?', callback_data=callback_data)],
            ])
        await self.send_message(message)


class ProcessMessageReload(BaseProcessMessage):

    async def process_message(self):
        message = await self.load_video(self.msg)
        await self.send_message(message)

    async def load_video(self, video: str) -> str:
        try:
            stream = await self.fetch_stream(video)
            query = videos.update().where(videos.c.url == video).values(download=False)
            async with self.engine.acquire() as connection:
                await connection.execute(query)
            return stream.default_filename
        except Exception as e:
            return str(e)


class ProcessMessageList(BaseProcessMessage):
    async def process_message(self):
        video_urls = await self.get_videos()
        for video in video_urls:
            message = await self.load_video(video)
            await self.send_message(message)


class ProcessMessageOne(BaseProcessMessage):
    async def process_message(self):
        message = await self.load_video(self.msg)
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
