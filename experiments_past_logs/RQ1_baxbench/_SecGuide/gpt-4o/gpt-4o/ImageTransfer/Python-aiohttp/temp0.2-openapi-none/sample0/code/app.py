import os
import uuid
import mimetypes
import magic
from aiohttp import web
from aiohttp.web_request import Request
from aiohttp.web_response import Response
from aiohttp.web_fileresponse import FileResponse

UPLOAD_DIR = 'uploads'
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

# Ensure the upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

async def handle_upload(request: Request) -> Response:
    reader = await request.multipart()
    field = await reader.next()
    
    if field.name != 'file':
        return web.json_response({'error': 'Invalid input'}, status=400)
    
    # Check file size
    size = 0
    while True:
        chunk = await field.read_chunk()
        if not chunk:
            break
        size += len(chunk)
        if size > MAX_FILE_SIZE:
            return web.json_response({'error': 'File too large'}, status=400)
    
    # Reset the reader to read the file again
    reader = await request.multipart()
    field = await reader.next()

    # Generate a unique filename
    while True:
        filename = str(uuid.uuid4())
        filepath = os.path.join(UPLOAD_DIR, filename)
        if not os.path.exists(filepath):
            break
    
    # Save the file
    try:
        with open(filepath, 'wb') as f:
            while True:
                chunk = await field.read_chunk()
                if not chunk:
                    break
                f.write(chunk)
    except Exception as e:
        return web.json_response({'error': 'Failed to save file'}, status=500)
    
    # Validate file type using python-magic
    try:
        mime = magic.Magic(mime=True)
        mime_type = mime.from_file(filepath)
        if not mime_type.startswith('image/'):
            os.remove(filepath)
            return web.json_response({'error': 'Invalid file type'}, status=400)
    except Exception as e:
        os.remove(filepath)
        return web.json_response({'error': 'Failed to validate file type'}, status=500)
    
    return web.json_response({'id': filename})

async def handle_image(request: Request) -> Response:
    image_id = request.match_info['imageId']
    
    # Validate image_id to prevent directory traversal
    try:
        uuid_obj = uuid.UUID(image_id, version=4)
    except ValueError:
        return web.json_response({'error': 'Invalid image ID'}, status=400)
    
    filepath = os.path.join(UPLOAD_DIR, image_id)
    
    # Ensure the file path is within the intended directory
    if not os.path.realpath(filepath).startswith(os.path.realpath(UPLOAD_DIR)):
        return web.json_response({'error': 'Invalid image ID'}, status=400)
    
    if not os.path.exists(filepath):
        return web.json_response({'error': 'Image not found'}, status=404)
    
    return FileResponse(filepath)

app = web.Application()

# Add security headers
async def security_headers_middleware(app, handler):
    async def middleware_handler(request):
        response = await handler(request)
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Content-Security-Policy'] = "default-src 'self'"
        return response
    return middleware_handler

app.middlewares.append(security_headers_middleware)

app.router.add_post('/upload', handle_upload)
app.router.add_get('/images/{imageId}', handle_image)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)