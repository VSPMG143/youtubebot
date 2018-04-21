import logging

import telepot
from secret import TELEGRAM_TOKEN


LOG_FORMAT = '%(levelname)-8s [%(asctime)s] %(message)s'
LOG_LEVEL = logging.DEBUG
LOG_FILENAME = 'log.log'

DB_NAME = 'youtube.sqlite3'

bot = telepot.Bot(TELEGRAM_TOKEN)

