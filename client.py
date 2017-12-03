import os
from urllib.parse import urljoin

import aiohttp
import asyncio

from pytube import YouTube


SERVER_URL = os.environ.get('SERVER_URL') 

async def main():
    async with aiohttp.ClientSession() as session:
        async with session.get(SERVER_URL) as response:
            videos = await response.json()
            for video in videos['videos']:
                try:
                    yt = YouTube(video[2])
                    yt_video = yt.get('mp4', '720p')
                    yt_video.download('/home/neri/downloads')  
                    print('Success download!', video[2])  
                except Exception as e:
                    print(e, video[2])
                finally:
                    await session.post(urljoin(SERVER_URL, 'update'), json={'url': video[2]})
                    print('Success update!', video[2])


loop = asyncio.get_event_loop()
loop.run_until_complete(main())

