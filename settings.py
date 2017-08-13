import logging
import os


TOKEN = os.environ.get('TELEGRAM_TOKEN')

LOG_FORMAT = '%(levelname)-8s [%(asctime)s] %(message)s'
LOG_LEVEL = logging.DEBUG
LOG_FILENAME = 'log.log'
