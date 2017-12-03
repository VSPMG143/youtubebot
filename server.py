import aiosqlite
from aiohttp import web


async def get_new_videos(request):
    async with aiosqlite.connect('youtube.sqlite3') as db:
        cursor = await db.execute(
            "SELECT * FROM videos WHERE download = 0"
        )
        videos = []
        async for row in cursor:
            videos.append(row)
    return web.json_response({'videos': videos})


async def update_video(request):
    url = request.match_info.get('url', '')
    print('Try to update: ', url)
    async with aiosqlite.connect('youtube.sqlite3') as db: 
        await db.execute('UPDATE videos SET download = 1 WHERE url = ?', (url,))
        await db.commit()
    return web.json_response({'status': 'ok'})


app = web.Application()
app.router.add_get('/', get_new_videos)
app.router.add_post('/update', update_video)
web.run_app(app, host='0.0.0.0', port=8080)

