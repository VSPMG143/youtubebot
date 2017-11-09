import aiohttp
import asyncio


async def fetch(session, url):
    with async_timeout.timeout(10):
        async with session.get(url) as response:
            videos = await response.text()
            asyncio.gather(*videos, return_exceptions=False)


async def main():
    async with aiohttp.ClientSession() as session:
        await fetch(session, 'http://python.org')


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
