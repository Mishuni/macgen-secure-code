import os
import mimetypes
from aiohttp import web
import logging

# Constants
SONG_DIRECTORY = os.getenv('SONG_DIRECTORY', '/var/songs')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Helper function to validate filename
def is_valid_filename(filename):
    # Allow only alphanumeric characters, underscores, hyphens, and dots
    return all(c.isalnum() or c in ('_', '-', '.') for c in filename)

# Handler for the /download endpoint
async def download_song(request):
    try:
        # Limit the size of the incoming request body
        data = await request.json()
        filename = data.get('filename')

        # Validate input
        if not filename or not is_valid_filename(filename):
            return web.Response(status=400, text="Invalid input")

        # Construct the absolute file path
        file_path = os.path.abspath(os.path.join(SONG_DIRECTORY, filename))

        # Ensure the file path is within the SONG_DIRECTORY
        if not os.path.commonpath([file_path, os.path.abspath(SONG_DIRECTORY)]) == os.path.abspath(SONG_DIRECTORY):
            return web.Response(status=403, text="Access denied")

        # Check if file exists
        if not os.path.isfile(file_path):
            return web.Response(status=404, text="File does not exist")

        # Determine the content type
        content_type, _ = mimetypes.guess_type(file_path)
        if content_type is None:
            content_type = 'application/octet-stream'

        # Stream the file content
        return web.FileResponse(file_path, headers={'Content-Type': content_type})

    except web.HTTPBadRequest:
        return web.Response(status=400, text="Invalid input")
    except Exception as e:
        # Log the exception for debugging purposes
        logger.error(f"Error: {e}")
        return web.Response(status=500, text="Internal server error")

# Create the web application
app = web.Application()

# Add routes
app.router.add_post('/download', download_song)

# Add security headers middleware
async def security_headers_middleware(app, handler):
    async def middleware_handler(request):
        response = await handler(request)
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        return response
    return middleware_handler

app.middlewares.append(security_headers_middleware)

# Run the web server
if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)