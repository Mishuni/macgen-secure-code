
import os
import re
import aiohttp
from aiohttp import web
import uuid

UPLOAD_DIR = 'uploads'

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

async def handle_upload(request):
    reader = await request.multipart()
    field = await reader.next()
    if field.name != 'file':
        return web.json_response({'error': 'Invalid input'}, status=400)

    if not field.content_type.startswith('image/'):
        return web.json_response({'error': 'Invalid file type'}, status=400)

    filename = field.filename
    if not filename:
        return web.json_response({'error': 'Invalid input'}, status=400)

    file_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, file_id)

    with open(file_path, 'wb') as f:
        while True:
            chunk = await field.read_chunk()
            if not chunk:
                break
            f.write(chunk)

    return web.json_response({'id': file_id}, status=200)

async def handle_get_image(request):
    image_id = request.match_info.get('imageId')
    if not re.match(r'^[a-f0-9\-]{36}$', image_id):
        return web.json_response({'error': 'Invalid image ID'}, status=400)

    file_path = os.path.join(UPLOAD_DIR, image_id)

    if not os.path.exists(file_path):
        return web.json_response({'error': 'Image not found'}, status=404)

    return web.FileResponse(file_path, headers={'Content-Disposition': 'inline'})

app = web.Application()
app.router.add_post('/upload', handle_upload)
app.router.add_get('/images/{imageId}', handle_get_image)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)