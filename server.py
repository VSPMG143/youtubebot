import asyncio
from datetime import date

from aiopg.sa import create_engine
from aiohttp import web

from db import videos
from secret import *


async def init_pg(app):
    app['engine'] = await create_engine(
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        loop=asyncio.get_event_loop()
    )


async def close_pg(app):
    app['engine'].close()


async def get_new_videos(request):
    query = videos.select().where(videos.c.download == False)
    async with app['engine'].acquire() as connection:
        res = []
        async for row in connection.execute(query):
            res.append({'name': row.name, 'url': row.url})
    return web.json_response({'videos': res})


async def update_video(request):
    data = await request.json()
    query = videos.update().where(videos.c.url == data.get('url', '')).values(download=True)
    async with app['engine'].acquire() as connection:
        await connection.execute(query)
    return web.json_response({'status': 'ok'})


async def update_videos(request):
    data = await request.json()
    query = videos.update().where(videos.c.updated == data.get('date', date.today())).values(download=True)
    async with app['engine'].acquire() as connection:
        await connection.execute(query)
    return web.json_response({'status': 'ok'})


async def create_video(request):
    data = await request.json()
    filename, url = data.get('filename'), data.get('url')
    if not filename or not url:
        return web.json_response({'status': 'error'})
    query = videos.insert().values(name=filename, url=url)
    async with app['engine'].acquire() as connection:
        await connection.execute(query)
    return web.json_response({'status': 'ok'})


if __name__ == '__main__':
    app = web.Application()
    app.on_startup.append(init_pg)
    app.on_cleanup.append(close_pg)
    app.router.add_get('/', get_new_videos)
    app.router.add_post('/update', update_video)
    app.router.add_post('/update_by_date', update_videos)
    web.run_app(app, host='0.0.0.0', port=8080)
