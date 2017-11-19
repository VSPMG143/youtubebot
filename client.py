import os

import aiohttp
import asyncio

from pytube import YouTube


SERVER_URL = os.environ.get('SERVER_URL') 

async def main():
    async with aiohttp.ClientSession() as session:
        async with session.get(SERVER_URL) as response:
            videos = await response.json()
            for video in videos:
                yt = YouTube(video[2])
                yt_video = yt.get('mp4', '720p')
                yt_video.download('/home/neri/downloads')    
                session.post(SERVER_URL + 'update', json={'url'=video[2]})


loop = asyncio.get_event_loop()
loop.run_until_complete(main())

