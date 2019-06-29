import logging.config

from pytube import YouTube, Stream
from telegram import Bot, MessageEntity
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram.utils.request import Request

from secret import *
from settings import LOGGING, DOWNLOAD_PATH, PROXY_URL

logging.config.dictConfig(LOGGING)
logger = logging.getLogger('youtubebot')


def get_stream(yt: YouTube) -> Stream:

    streams = yt.streams.filter(
        file_extension='mp4', type='video'
    ).order_by('resolution').desc().all()

    for stream in streams:
        if stream.includes_audio_track and stream.resolution <= '720p':
            return stream
    return yt.streams.first()


def start(update, context):
    update.send_message(
        chat_id=context.message.chat.id, text='Hi!'
    )


def download_youtube_video(update, context):
    logger.debug('download_youtube_video')
    try:
        yt = YouTube(context.message.text)
        logger.debug(yt)
        stream = get_stream(yt)
        logger.debug(stream)
        stream.download(DOWNLOAD_PATH)
        logger.info('Success download $s', yt.title)
        update.send_message(
            chat_id=context.message.chat.id, text=f'Success download video {yt.title}'
        )
    except OSError:
        logger.error('This video is exist %s', yt.title)
        update.send_message(
            chat_id=context.message.chat.id, text=f'This video is exist {yt.title}'
        )
    except Exception as e:
        logger.error('Update "%s" caused error "%s"', update, e)
        update.send_message(
            chat_id=context.message.chat.id, text=f'Update {update} caused error {e}'
        )


def echo(update, context):
    logger.debug('echo')
    try:
        update.send_message(chat_id=context.message.chat.id, text=context.message.text)
    except Exception as e:
        logger.error('Update "%s" caused error "%s"', update, context.error)


def error(update, context):
    logger.error('Update "%s" caused error "%s"', update, context.error)


def run():
    request = Request(proxy_url=PROXY_URL)
    bot = Bot(TELEGRAM_TOKEN, request=request)
    updater = Updater(bot=bot)
    dp = updater.dispatcher

    dp.add_handler(
        MessageHandler(
            Filters.text & (Filters.entity(MessageEntity.URL)), download_youtube_video
        )
    )

    dp.add_handler(MessageHandler(Filters.text, echo))

    dp.add_handler(CommandHandler('start', start))

    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    run()
