import sys
import asyncio
from aiohttp import web
import aiohttp_cors  # CORS middleware
from scraper_api import get_cached_data  # Import the caching wrapper

# Windows-specific asyncio policy
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

routes = web.RouteTableDef()

@routes.get('/nifty')
async def get_nifty(request):
    data = await get_cached_data()
    if data is None:
        return web.json_response({'error': 'Scraping failed. Please try again later.'}, status=502)
    return web.json_response(data)

app = web.Application()
app.add_routes(routes)

# CORS setup
cors = aiohttp_cors.setup(app, defaults={
    "*": aiohttp_cors.ResourceOptions(
        allow_credentials=True,
        expose_headers="*",
        allow_headers="*",
    )
})

# Apply CORS to each route
for route in list(app.router.routes()):
    cors.add(route)

if __name__ == '__main__':
    web.run_app(app, host='127.0.0.1', port=8000)