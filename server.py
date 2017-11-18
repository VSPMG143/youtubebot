import aiosqlite
from aiohttp import web


async def get_new_videos(request):
    async with aiosqlite.connect('youtube.sqlite3') as db:
        cursor = await db.execute(
            "SELECT * FROM videos WHERE download=0"
        )
        videos = []
        async for row in cursor:
            videos.append(row)
    return web.json_response({'videos': videos})


app = web.Application()
app.router.add_get('/', get_new_videos)

web.run_app(app, host='0.0.0.0', port=8080)

