from urlparse import urlparse

from pytube import YouTube

from db import c


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

def check_url_in_db(url):
    c.execute("SELECT EXISTS(SELECT id FROM videos WHERE url='%s');" % url)
