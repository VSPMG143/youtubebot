import asyncio
import os
from urllib.parse import urljoin

import aiohttp
from pytube import YouTube

from db import Video
from utils import get_stream

SERVER_URL = os.environ.get('SERVER_URL') 

async def main():
    async with aiohttp.ClientSession() as session:
        async with session.get(SERVER_URL) as response:
            videos = await response.json()
            for video in videos['videos']:
                video = Video(*video)
                try:
                    yt = YouTube(video.url)
                    stream = get_stream(yt)
                    stream.download('/home/neri/downloads')
                    print('Success download!', video.name)
                except Exception as e:
                    print(e, video.url)
                finally:
                    await session.post(urljoin(SERVER_URL, 'update'), json={'url': video.url})
                    print('Success update!', video.name)


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
