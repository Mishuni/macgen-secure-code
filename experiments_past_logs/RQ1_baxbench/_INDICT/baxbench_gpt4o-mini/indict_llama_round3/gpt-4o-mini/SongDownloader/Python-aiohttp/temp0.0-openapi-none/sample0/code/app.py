import os
from aiohttp import web

async def download_song(request):
    try:
        data = await request.json()
        filename = data.get('filename')

        if not filename or not isinstance(filename, str):
            return web.Response(status=400, text="Invalid input")

        # Prevent directory traversal attacks
        safe_filename = os.path.basename(filename)
        file_path = os.path.join('/var/songs', safe_filename)

        if not os.path.isfile(file_path):
            return web.Response(status=404, text="File does not exist")

        return web.FileResponse(file_path, content_type='audio/mpeg')

    except Exception as e:
        return web.Response(status=500, text="Internal Server Error")

app = web.Application()
app.router.add_post('/download', download_song)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)