
import os
import re
from aiohttp import web

# Directory where songs are stored
SONG_DIRECTORY = '/var/songs'

async def download_song(request):
    try:
        data = await request.json()
        filename = data.get('filename', '').strip()

        # Validate and sanitize filename input
        if not re.match(r'^[\w,\s-]+\.[A-Za-z]{3}$', filename):
            return web.Response(status=400, text='Invalid filename')

        # Construct the full path to the song file
        file_path = os.path.join(SONG_DIRECTORY, filename)

        # Restrict file access to the allowed directory
        if not os.path.abspath(file_path).startswith(os.path.abspath(SONG_DIRECTORY)):
            return web.Response(status=400, text='Invalid file path')

        # Check if the file exists and is a regular file
        if not os.path.isfile(file_path):
            return web.Response(status=404, text='File does not exist')

        # Stream the content of the song
        return web.FileResponse(file_path, headers={'Content-Type': 'audio/mpeg'})

    except Exception as e:
        return web.Response(status=400, text='Invalid input')

app = web.Application()
app.router.add_post('/download', download_song)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)