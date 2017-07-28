from urlparse import urlparse

from pytube import YouTube

from db import check_url, insert_row


def process_message(msg):
    if urlparse(msg).netloc == 'youtube.com' and not check_url(msg):
        try:
            yt = YouTube(msg)
            video = yt.get('mp4', '720p')
            video.download('/home/neri/downloads')
            insert_row(video.filename, msg)
            message = video.filename
        except Exception as e:
            message = str(e)
    else:
        message = msg    
    return message
