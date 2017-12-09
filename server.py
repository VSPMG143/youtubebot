import aiopg
from aiohttp import web

from secret import DSN


async def init_pg(app):
    app['conn'] = await aiopg.connect(DSN)
    return app


async def close_pg(app):
    app['conn'].close()


async def get_new_videos(request):
    cursor = await app['conn'].cursor()
    await cursor.execute(
        "SELECT * FROM videos WHERE download = false"
    )
    videos = []
    async for row in cursor:
        videos.append(row)
    return web.json_response({'videos': videos})


async def update_video(request):
    cursos = await app['db'].cursor()
    url = request.match_info.get('url', '')
    await cursor.execute('UPDATE videos SET download = 1 WHERE url = (%s)', (url,))
    await cursor.commit()
    return web.json_response({'status': 'ok'})


app = web.Application()
app.on_startup.append(init_pg)
app.on_cleanup.append(close_pg)
app.router.add_get('/', get_new_videos)
app.router.add_post('/update', update_video)
web.run_app(app, host='0.0.0.0', port=8080)

