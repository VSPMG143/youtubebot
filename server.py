from aiohttp import web
import aioodbc


async def init_db(app):
    dsn = 'Driver=SQLite;Database=youtubebot.sqlite'
    conn = await aioodbc.connect(dsn=dsn)
    cur = await conn.cursor()
    app['conn'] = conn
    app['cursor'] = cur


async def handle(request):
    await videos app['cursor'].execute(
        "SELECT * FROM videos"
    )
    return web.json_response({'videos': videos})


async def close_db(app):
    await app['conn'].close()
    await app['cursor'].close()


app = web.Application()
app.on_startup.append(init_db)
app.on_cleanup.append(close_db)
app.router.add_get('/', handle)

web.run_app(app, host='0.0.0.0', port=8080)

