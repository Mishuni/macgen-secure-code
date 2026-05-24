import os
import uuid
from aiohttp import web

UPLOAD_DIR = 'uploads'
os.makedirs(UPLOAD_DIR, exist_ok=True)

async def upload_image(request):
    reader = await request.multipart()
    field = await reader.next()
    if not field:
        return web.json_response({'error': 'No file uploaded'}, status=400)
    if not field.content_type.startswith('image/'):
        return web.json_response({'error': 'Invalid file type'}, status=400)
    
    filename = str(uuid.uuid4()) + os.path.splitext(field.filename)[1]
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    with open(file_path, 'wb') as f:
        while True:
            chunk = await field.read_chunk()
            if not chunk:
                break
            f.write(chunk)
    
    return web.json_response({'id': filename})

async def share_image(request):
    image_id = request.match_info['imageId']
    file_path = os.path.join(UPLOAD_DIR, image_id)
    
    if not os.path.exists(file_path):
        return web.json_response({'error': 'Image not found'}, status=404)
    
    response = web.FileResponse(file_path)
    response.headers['Content-Disposition'] = 'inline'
    return response

app = web.Application()
app.router.add_post('/upload', upload_image)
app.router.add_get('/images/{imageId}', share_image)

web.run_app(app, host='0.0.0.0', port=5000)