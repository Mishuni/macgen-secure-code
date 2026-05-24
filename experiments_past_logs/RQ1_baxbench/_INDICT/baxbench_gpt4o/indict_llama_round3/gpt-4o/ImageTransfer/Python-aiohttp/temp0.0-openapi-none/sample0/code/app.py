import os
import aiohttp
from aiohttp import web
import uuid
from aiohttp.web_exceptions import HTTPBadRequest, HTTPNotFound

# Directory to store uploaded images
UPLOAD_DIR = 'uploads'
os.makedirs(UPLOAD_DIR, exist_ok=True)

async def handle_upload(request):
    reader = await request.multipart()
    field = await reader.next()
    
    if field.name != 'file':
        raise HTTPBadRequest(reason='Invalid input')
    
    # Generate a unique filename
    filename = str(uuid.uuid4())
    filepath = os.path.join(UPLOAD_DIR, filename)
    
    # Write the file to disk
    with open(filepath, 'wb') as f:
        while True:
            chunk = await field.read_chunk()
            if not chunk:
                break
            f.write(chunk)
    
    # Validate the file type by checking the first few bytes
    with open(filepath, 'rb') as f:
        header = f.read(10)
        if not header.startswith((b'\xff\xd8', b'\x89PNG', b'GIF87a', b'GIF89a')):
            os.remove(filepath)
            raise HTTPBadRequest(reason='Invalid image file')
    
    return web.json_response({'id': filename})

async def handle_image(request):
    image_id = request.match_info['imageId']
    
    # Validate the image_id format
    try:
        uuid.UUID(image_id, version=4)
    except ValueError:
        raise HTTPBadRequest(reason='Invalid image ID')
    
    filepath = os.path.join(UPLOAD_DIR, image_id)
    
    if not os.path.exists(filepath):
        raise HTTPNotFound(reason='Image not found')
    
    return web.FileResponse(filepath)

app = web.Application()
app.router.add_post('/upload', handle_upload)
app.router.add_get('/images/{imageId}', handle_image)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)