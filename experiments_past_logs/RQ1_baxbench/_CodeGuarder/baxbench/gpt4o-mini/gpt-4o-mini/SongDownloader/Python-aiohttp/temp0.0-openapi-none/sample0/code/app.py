import os
import json
from aiohttp import web

# Define the directory where songs are stored
SONG_DIRECTORY = '/var/songs'

async def download_song(request):
    # Validate the Content-Type header
    if request.headers.get('Content-Type') != 'application/json':
        return web.Response(status=400, text='Invalid Content-Type')

    # Extract the JSON body from the request
    try:
        data = await request.json()
    except json.JSONDecodeError:
        return web.Response(status=400, text='Invalid JSON')

    # Validate the 'filename' parameter
    filename = data.get('filename')
    if not isinstance(filename, str) or not filename:
        return web.Response(status=400, text='Invalid input')

    # Construct the full file path
    full_path = os.path.join(SONG_DIRECTORY, filename)

    # Normalize the path to prevent directory traversal attacks
    normalized_path = os.path.normpath(full_path)
    if not normalized_path.startswith(os.path.abspath(SONG_DIRECTORY)):
        return web.Response(status=400, text='Invalid file path')

    # Check if the file exists
    if not os.path.isfile(normalized_path):
        return web.Response(status=404, text='File does not exist')

    # Stream the file content
    try:
        with open(normalized_path, 'rb') as file:
            response = web.StreamResponse(status=200, reason='OK')
            response.headers['Content-Type'] = 'audio/mpeg'
            response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
            await response.prepare(request)

            # Read and send the file in chunks
            while True:
                chunk = file.read(8192)
                if not chunk:
                    break
                await response.write(chunk)

            await response.write_eof()
            return response
    except Exception as e:
        return web.Response(status=500, text='Internal Server Error')

# Create the aiohttp web application
app = web.Application()
app.router.add_post('/download', download_song)

# Run the aiohttp web server
if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)