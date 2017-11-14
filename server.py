import aiosqlite
from aiohttp import web


async def init_db(app):
    async with aiosqlite.connect('youtube.sqlite3') as db:
        cur = await db.cursor()
        app['cursor'] = cur


async def handle(request):
    async with aiosqlite.connect('youtube.sqlite3') as db:
        cursor = await db.execute(
            "SELECT * FROM videos"
        )
        videos = []
        async for row in cursor:
            videos.append(row)
    return web.json_response({'videos': videos})

async def close_db(app):
    await app['cursor'].close()


app = web.Application()
#app.on_startup.append(init_db)
#app.on_cleanup.append(close_db)
app.router.add_get('/', handle)

web.run_app(app, host='0.0.0.0', port=8080)

