import logging
import pathlib

LOG_FORMAT = '%(levelname)-8s [%(asctime)s] %(message)s'
LOG_LEVEL = logging.DEBUG
LOG_FILENAME = 'log.log'

DB_NAME = 'youtube.sqlite3'


DOWNLOAD_PATH = pathlib.PosixPath(pathlib.Path().home(), pathlib.Path('Movies'))

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
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'base',
        }
    },
    'loggers': {
        'youtubebot': {
            'level': 'DEBUG',
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
