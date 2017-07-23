import os
import time

import telepot
from telepot.loop import MessageLoop
from pytube import YouTube


def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    print(content_type, chat_type, chat_id)

    if content_type == 'text':
        if msg['text'].startswith('https://www.youtube.com/'):
            try:
                yt = YouTube(msg['text'])
                video = yt.get('mp4', '720p')
                video.download('/home/neri/downloads')
                message = video.filename
            except Exception as e:
                message = str(e)
        else:
            message = msg['text']    
        bot.sendMessage(chat_id, message)

TOKEN = os.environ.get('TELEGRAM_TOKEN')

bot = telepot.Bot(TOKEN)
MessageLoop(bot, handle).run_as_thread()

while 1:
    time.sleep(10)
