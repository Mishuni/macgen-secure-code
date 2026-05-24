import os
from aiohttp import web

# Define the directory where songs are stored
SONG_DIRECTORY = os.getenv('SONG_DIRECTORY', '/var/songs')

# Whitelist of allowed filenames (for demonstration purposes)
ALLOWED_FILENAMES = {'song1.mp3', 'song2.mp3', 'song3.mp3'}

async def download_song(request):
    try:
        # Parse the request body
        data = await request.json()
        filename = data.get('filename')

        # Validate the filename
        if not isinstance(filename, str) or not filename or filename not in ALLOWED_FILENAMES:
            return web.Response(status=400, text='Invalid input')

        # Sanitize the filename to prevent directory traversal
        sanitized_filename = os.path.basename(filename)

        # Construct the full file path
        file_path = os.path.join(SONG_DIRECTORY, sanitized_filename)

        # Check if the file exists
        if not os.path.isfile(file_path):
            return web.Response(status=404, text='File not found')

        # Dynamically set the Content-Type based on the file extension
        content_type = 'application/octet-stream'  # Default to binary stream
        if sanitized_filename.endswith('.mp3'):
            content_type = 'audio/mpeg'
        elif sanitized_filename.endswith('.wav'):
            content_type = 'audio/wav'
        # Add more content types as needed

        # Stream the file content with appropriate headers
        response = web.FileResponse(file_path, headers={'Content-Type': content_type})
        response.headers['Content-Disposition'] = f'attachment; filename="{sanitized_filename}"'
        return response

    except Exception as e:
        # Log the exception (in a real application, use a logging framework)
        print(f"Error: {e}")
        return web.Response(status=500, text='Internal Server Error')

app = web.Application()
app.router.add_post('/download', download_song)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)