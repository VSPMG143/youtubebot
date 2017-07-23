import os
import time

import telepot
from telepot.loop import MessageLoop
from redis import Redis
from rq import Queue

from helpers import process_message


def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    print(content_type, chat_type, chat_id)

    if content_type == 'text':
        job = q.enqueue(process_message, msg['text'])
        bot.sendMessage(chat_id, job.return_value)


q = Queue(connection=Redis())


TOKEN = os.environ.get('TELEGRAM_TOKEN')
bot = telepot.Bot(TOKEN)
MessageLoop(bot, handle).run_as_thread()

while 1:
    time.sleep(10)
