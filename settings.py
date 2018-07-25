import logging

import telepot
from secret import TELEGRAM_TOKEN


LOG_FORMAT = '%(levelname)-8s [%(asctime)s] %(message)s'
LOG_LEVEL = logging.DEBUG
LOG_FILENAME = 'log.log'

DB_NAME = 'youtube.sqlite3'

bot = telepot.Bot(TELEGRAM_TOKEN)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'base': {
            'format': '%(asctime)s %(levelname)s %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'base',
        }
    },
    'loggers': {
        'youtubebot': {
            'level': 'INFO',
            'handlers': ['console'],
            'propagate': False,
        },
        'asyncio': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        }
    },
    'root': {
        'level': 'ERROR',
        'handlers': ['console'],
    }
}
