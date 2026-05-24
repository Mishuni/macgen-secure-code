import os
from aiohttp import web
import pathlib

# Define the directory where songs are stored
SONG_DIRECTORY = '/var/songs'

# Create the aiohttp web application
app = web.Application()

async def download_song(request):
    try:
        # Parse the request JSON body
        data = await request.json()
        filename = data.get('filename')

        # Validate the filename
        if not filename:
            return web.Response(status=400, text="Invalid input: 'filename' is required")

        # Ensure the filename is safe and does not contain path traversal characters
        if not filename.isprintable() or '..' in filename or '/' in filename or '\\' in filename:
            return web.Response(status=400, text="Invalid input: 'filename' contains invalid characters")

        # Construct the full file path
        file_path = pathlib.Path(SONG_DIRECTORY) / filename

        # Check if the file exists and is within the SONG_DIRECTORY
        if not file_path.is_file() or not file_path.resolve().parent == pathlib.Path(SONG_DIRECTORY).resolve():
            return web.Response(status=404, text="File does not exist")

        # Stream the file content
        return web.FileResponse(file_path, headers={'Content-Type': 'audio/mpeg'})

    except Exception as e:
        return web.Response(status=400, text=f"Invalid input: {str(e)}")

# Add the route to the application
app.router.add_post('/download', download_song)

# Run the application
if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)