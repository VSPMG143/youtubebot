from pytube import YouTube, Stream

from settings import DOWNLOAD_PATH


def get_stream(yt: YouTube) -> Stream:
    streams = yt.streams.filter(
        file_extension='mp4', type='video'
    ).order_by('resolution').desc()
    for stream in streams:
        if stream.includes_audio_track and stream.resolution <= '720p':
            return stream
    return yt.streams.first()


def load(url):
    yt = YouTube(url)
    stream = get_stream(yt)
    stream.download(DOWNLOAD_PATH)


if __name__ == '__main__':
    load('https://www.youtube.com/watch?v=DTpZaQJUm24')
