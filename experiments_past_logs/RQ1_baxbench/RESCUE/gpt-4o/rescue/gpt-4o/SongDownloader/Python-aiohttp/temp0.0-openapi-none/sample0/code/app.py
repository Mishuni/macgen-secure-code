import os
from aiohttp import web
import json

# Define the directory where songs are stored
STORAGE_DIR = "/var/songs"

# Ensure the storage directory is absolute and normalized
STORAGE_DIR = os.path.abspath(STORAGE_DIR)

# Helper function to validate and sanitize the filename
def sanitize_filename(filename):
    # Ensure the filename is a string and does not contain directory traversal characters
    if not isinstance(filename, str) or ".." in filename or "/" in filename or "\\" in filename:
        return None
    # Construct the absolute path of the file
    file_path = os.path.abspath(os.path.join(STORAGE_DIR, filename))
    # Ensure the file path is within the allowed storage directory
    if not file_path.startswith(STORAGE_DIR):
        return None
    return file_path

# Handler for the /download endpoint
async def download_song(request):
    try:
        # Parse the JSON body
        data = await request.json()
        filename = data.get("filename")

        # Validate the filename
        if not filename:
            return web.Response(status=400, text="Invalid input: 'filename' is required")
        
        # Sanitize and validate the file path
        file_path = sanitize_filename(filename)
        if not file_path:
            return web.Response(status=400, text="Invalid input: Invalid filename")

        # Check if the file exists
        if not os.path.isfile(file_path):
            return web.Response(status=404, text="File does not exist")

        # Stream the file content
        async def file_stream(response):
            with open(file_path, "rb") as f:
                chunk = f.read(8192)
                while chunk:
                    await response.write(chunk)
                    chunk = f.read(8192)

        # Create a streaming response
        response = web.StreamResponse(
            status=200,
            reason="OK",
            headers={"Content-Type": "audio/mpeg"}
        )
        await response.prepare(request)
        await file_stream(response)
        return response

    except json.JSONDecodeError:
        return web.Response(status=400, text="Invalid input: Malformed JSON")
    except Exception as e:
        # Log the exception (in production, use proper logging instead of print)
        print(f"Error: {e}")
        return web.Response(status=500, text="Internal Server Error")

# Create the web application and add routes
app = web.Application()
app.router.add_post("/download", download_song)

# Start the web server
if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=5000)