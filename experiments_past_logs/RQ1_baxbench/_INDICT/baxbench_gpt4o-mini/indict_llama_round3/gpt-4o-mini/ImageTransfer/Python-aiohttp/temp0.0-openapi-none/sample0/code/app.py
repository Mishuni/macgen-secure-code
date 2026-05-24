import aiohttp
from aiohttp import web
import os
import uuid

# Directory to store uploaded images
UPLOAD_DIR = 'uploads'

# Ensure the upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

async def upload_image(request):
    # Handle image upload
    reader = await request.multipart()
    field = await reader.next()
    
    if field is None:
        return web.json_response({'error': 'No file uploaded'}, status=400)

    # Validate file type (basic check for image formats)
    if not field.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp')):
        return web.json_response({'error': 'Invalid file type'}, status=400)

    # Save the uploaded file
    filename = f"{uuid.uuid4()}{os.path.splitext(field.filename)[1]}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    try:
        with open(filepath, 'wb') as f:
            while True:
                chunk = await field.read_chunk()  # 512 bytes by default
                if not chunk:
                    break
                f.write(chunk)
    except Exception as e:
        return web.json_response({'error': str(e)}, status=500)

    return web.json_response({'id': filename})

async def share_image(request):
    image_id = request.match_info['imageId']
    filepath = os.path.join(UPLOAD_DIR, image_id)

    if not os.path.exists(filepath):
        return web.json_response({'error': 'Image not found'}, status=404)

    # Determine the content type based on the file extension
    content_type = 'application/octet-stream'
    if image_id.lower().endswith('.png'):
        content_type = 'image/png'
    elif image_id.lower().endswith('.jpg') or image_id.lower().endswith('.jpeg'):
        content_type = 'image/jpeg'
    elif image_id.lower().endswith('.gif'):
        content_type = 'image/gif'
    elif image_id.lower().endswith('.bmp'):
        content_type = 'image/bmp'
    elif image_id.lower().endswith('.webp'):
        content_type = 'image/webp'

    return web.FileResponse(filepath, headers={'Content-Type': content_type})

app = web.Application()
app.router.add_post('/upload', upload_image)
app.router.add_get('/images/{imageId}', share_image)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)