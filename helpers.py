import os
from urllib.parse import urlparse

import telepot
from pytube import YouTube

from db import check_url, insert_row


TOKEN = os.environ.get('TELEGRAM_TOKEN')
bot = telepot.Bot(TOKEN)


def process_message(msg, chat_id):
    if urlparse(msg).netloc == 'www.youtube.com' and check_url(msg):
        try:
            yt = YouTube(msg)
            video = yt.get('mp4', '720p')
            video.download('/home/neri/downloads')
            print('success!')
            insert_row((video.filename, msg))
            message = video.filename
        except Exception as e:
            message = str(e)
    else:
        message = msg
    bot.sendMessage(chat_id, message)
