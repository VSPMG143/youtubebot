import asyncio
import os
from urllib.parse import urljoin

import aiohttp
from pytube import YouTube

SERVER_URL = os.environ.get('SERVER_URL') 


def get_stream(yt):
    streams = yt.streams.filter(file_extension='mp4', type='video').order_by('resolution').desc().all()
    for stream in streams:
        if stream.includes_audio_track and stream.resolution <= '720p':
            return stream
    return yt.streams.first()


async def main():
    async with aiohttp.ClientSession() as session:
        async with session.get(SERVER_URL) as response:
            videos = await response.json()
            for video in videos['videos']:
                try:
                    yt = YouTube(video['url'])
                    stream = get_stream(yt)
                    stream.download('/home/neri/downloads')
                    print('Success download!', video['name'])
                except OSError:
                    print('This video is exist! ', video['name'])
                except Exception as e:
                    print(e, video['url'])
                    continue
                await session.post(urljoin(SERVER_URL, 'update'), json={'url': video['url']})
                print('Success update!', video['name'])


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
