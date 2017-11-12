import time
from urllib.parse import urlparse

from telepot.loop import MessageLoop

from db import check_url, insert_row
from settings import *


def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    logging.info((content_type, chat_type, chat_id))

    if content_type == 'text':
        process_message(msg['text'], chat_id)


def process_message(msg, chat_id):
    if urlparse(msg).netloc == 'www.youtube.com' and check_url(msg):
        insert_row((video.filename, msg))
        message = video.filename
        logging.info('success!')
    else:
    	message = msg
    bot.sendMessage(chat_id, message)


logging.basicConfig(format=LOG_FORMAT, level=LOG_LEVEL , filename=LOG_FILENAME)


MessageLoop(bot, handle).run_as_thread()

while 1:
    time.sleep(10)
