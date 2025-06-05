import sys
import asyncio
from aiohttp import web
from scraper_api import get_cached_data  # Import the caching wrapper

# Force Windows-specific asyncio policy
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

routes = web.RouteTableDef()

@routes.get('/nifty')
async def get_nifty(request):
    data = await get_cached_data()  # Use cached data
    if data is None:
        return web.json_response({'error': 'Scraping failed. Please try again later.'}, status=502)
    return web.json_response(data)

app = web.Application()
app.add_routes(routes)

if __name__ == '__main__':
    web.run_app(app, host='127.0.0.1', port=8000)