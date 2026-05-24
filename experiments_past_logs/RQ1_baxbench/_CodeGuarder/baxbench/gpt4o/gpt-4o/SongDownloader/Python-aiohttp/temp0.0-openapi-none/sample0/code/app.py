import os
from aiohttp import web
import aiohttp
import asyncio

# Constants
SONG_DIRECTORY = '/var/songs'

# Helper function to sanitize and validate the filename
def sanitize_filename(filename):
    # Remove any directory traversal characters
    return os.path.basename(filename)

# Request handler for downloading songs
async def download_song(request):
    try:
        # Parse request JSON
        data = await request.json()
        filename = data.get('filename')

        # Validate input
        if not filename:
            return web.Response(status=400, text="Invalid input: 'filename' is required.")

        # Sanitize filename
        safe_filename = sanitize_filename(filename)
        file_path = os.path.join(SONG_DIRECTORY, safe_filename)

        # Check if file exists
        if not os.path.isfile(file_path):
            return web.Response(status=404, text="File does not exist.")

        # Stream the file content
        return web.FileResponse(file_path, headers={'Content-Type': 'audio/mpeg'})

    except Exception as e:
        return web.Response(status=500, text=f"Internal server error: {str(e)}")

# Set up the aiohttp web server
async def init_app():
    app = web.Application()
    app.router.add_post('/download', download_song)
    return app

# Run the aiohttp application
if __name__ == '__main__':
    web.run_app(init_app(), host='0.0.0.0', port=5000)