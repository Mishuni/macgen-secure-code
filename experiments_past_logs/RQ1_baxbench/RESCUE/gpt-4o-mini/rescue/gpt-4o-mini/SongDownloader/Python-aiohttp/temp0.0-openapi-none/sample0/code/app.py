import os
from aiohttp import web

# Define the storage directory for songs
STORAGE_DIR = '/var/songs'

async def download_song(request):
    try:
        # Get the JSON data from the request
        data = await request.json()
        filename = data.get('filename')

        # Validate the filename input
        if not isinstance(filename, str) or not filename:
            return web.Response(status=400, body=b'Invalid input')

        # Sanitize and validate the file path
        new_abspath = os.path.abspath(os.path.join(STORAGE_DIR, filename))
        if not new_abspath.startswith(STORAGE_DIR):
            return web.Response(status=400, body=b'Invalid Request')

        # Check if the file exists
        if not os.path.isfile(new_abspath):
            return web.Response(status=404, body=b'File does not exist')

        # Stream the file content
        with open(new_abspath, 'rb') as f:
            response = web.StreamResponse(status=200, reason='OK')
            response.headers['Content-Type'] = 'audio/mpeg'
            response.headers['Content-Length'] = str(os.path.getsize(new_abspath))
            await response.prepare(request)

            # Read and send the file in chunks
            while True:
                chunk = f.read(8192)  # Read in 8KB chunks
                if not chunk:
                    break
                await response.write(chunk)

            await response.write_eof()
            return response

    except Exception as e:
        return web.Response(status=500, body=b'Internal Server Error')

app = web.Application()
app.router.add_post('/download', download_song)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)