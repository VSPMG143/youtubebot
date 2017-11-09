from aiohttp import web


async def handle(request):
    name = request.match_info.get('chats', "1")
    return web.Response(name)


app = web.Application()
app.router.add_get('/', handle)

web.run_app(app, host='0.0.0.0', port=8080)
