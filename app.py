import time

import telepot
from telepot.loop import MessageLoop
from redis import Redis
from rq import Queue

from helpers import process_message
from settings import *


def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    print(content_type, chat_type, chat_id)
    logging.info((content_type, chat_type, chat_id))

    if content_type == 'text':
        job = q.enqueue(process_message, msg['text'], chat_id)

logging.basicConfig(format=LOG_FORMAT, level=LOG_LEVEL , filename=LOG_FILENAME)


q = Queue(connection=Redis())


bot = telepot.Bot(TOKEN)
MessageLoop(bot, handle).run_as_thread()

while 1:
    time.sleep(10)
