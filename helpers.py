from urlparse import urlparse

from pytube import YouTube


def process_message(msg):
    if urlparse(msg).netloc == 'youtube.com':
        try:
            yt = YouTube(msg)
            video = yt.get('mp4', '720p')
            video.download('/home/neri/downloads')
            message = video.filename
        except Exception as e:
            message = str(e)
    else:
        message = msg    
    return message
