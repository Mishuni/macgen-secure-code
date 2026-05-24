import aiohttp
from aiohttp import web
import re
from pathlib import Path

async def download_song(request):
    data = await request.json()
    filename = data.get('filename')
    
    # Validate Filename Input
    if not re.match(r'^[\w\-.]+$', filename):
        return web.Response(status=400, text='Invalid filename')
    
    # Use Safe File Handling
    file_path = Path('/var/songs') / filename
    if not file_path.is_file() or not file_path.resolve().startswith(Path('/var/songs').resolve()):
        return web.Response(status=404, text='File does not exist')
    
    return web.FileResponse(file_path)

app = web.Application()
app.router.add_post('/download', download_song)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)