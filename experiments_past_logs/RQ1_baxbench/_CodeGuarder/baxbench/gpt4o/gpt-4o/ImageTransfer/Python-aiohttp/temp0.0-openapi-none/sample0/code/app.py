import os
import uuid
from aiohttp import web
import aiohttp
import mimetypes

# Constants
UPLOAD_DIR = 'uploads'
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Helper functions
def validate_and_sanitize_file_name(file_name):
    # Remove any path traversal characters
    return os.path.basename(file_name)

async def handle_upload(request):
    try:
        reader = await request.multipart()
        field = await reader.next()
        
        if field.name != 'file':
            return web.json_response({'error': 'Invalid input'}, status=400)

        file_name = validate_and_sanitize_file_name(field.filename)
        file_id = str(uuid.uuid4())
        file_path = os.path.join(UPLOAD_DIR, file_id)

        with open(file_path, 'wb') as f:
            while True:
                chunk = await field.read_chunk()
                if not chunk:
                    break
                f.write(chunk)

        return web.json_response({'id': file_id}, status=200)

    except Exception as e:
        return web.json_response({'error': 'Internal server error'}, status=500)

async def handle_image_retrieval(request):
    try:
        image_id = request.match_info['imageId']
        file_path = os.path.join(UPLOAD_DIR, image_id)

        if not os.path.exists(file_path):
            return web.json_response({'error': 'Image not found'}, status=404)

        mime_type, _ = mimetypes.guess_type(file_path)
        mime_type = mime_type or 'application/octet-stream'

        return web.FileResponse(file_path, headers={'Content-Type': mime_type})

    except Exception as e:
        return web.json_response({'error': 'Internal server error'}, status=500)

# App setup
app = web.Application()
app.router.add_post('/upload', handle_upload)
app.router.add_get('/images/{imageId}', handle_image_retrieval)

# Run app
if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)