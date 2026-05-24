import os
import json
from aiohttp import web

# Directory to store uploaded images
UPLOAD_DIR = 'uploads'
os.makedirs(UPLOAD_DIR, exist_ok=True)

# In-memory storage for image identifiers
image_storage = {}

async def upload_image(request):
    if 'file' not in request.post():
        return web.json_response({'error': 'No file provided'}, status=400)

    # Get the uploaded file
    file = request.post()['file']
    if not file:
        return web.json_response({'error': 'Invalid file'}, status=400)

    # Sanitize the filename
    filename = file.filename
    if not filename or '/' in filename or '\\' in filename:
        return web.json_response({'error': 'Invalid file name'}, status=400)

    # Save the file
    file_path = os.path.join(UPLOAD_DIR, filename)
    try:
        with open(file_path, 'wb') as f:
            while True:
                chunk = await file.read(1024)
                if not chunk:
                    break
                f.write(chunk)
    except Exception as e:
        return web.json_response({'error': 'Internal server error'}, status=500)

    # Generate a unique identifier for the image
    image_id = filename  # In a real application, use a UUID or similar
    image_storage[image_id] = file_path

    return web.json_response({'id': image_id})

async def get_image(request):
    image_id = request.match_info['imageId']
    file_path = image_storage.get(image_id)

    if not file_path or not os.path.exists(file_path):
        return web.json_response({'error': 'Image not found'}, status=404)

    try:
        with open(file_path, 'rb') as f:
            content = f.read()
        return web.Response(body=content, content_type='image/jpeg')  # Adjust content type as needed
    except Exception as e:
        return web.json_response({'error': 'Internal server error'}, status=500)

app = web.Application()
app.router.add_post('/upload', upload_image)
app.router.add_get('/images/{imageId}', get_image)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)