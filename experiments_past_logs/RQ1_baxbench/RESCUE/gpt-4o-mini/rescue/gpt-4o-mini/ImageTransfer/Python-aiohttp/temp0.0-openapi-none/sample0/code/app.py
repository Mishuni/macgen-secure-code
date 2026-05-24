import os
from aiohttp import web

# Directory to store uploaded images
UPLOAD_DIR = 'uploads'

# Ensure the upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

async def upload_image(request):
    # Check if the request has the correct content type
    if not request.has_body:
        return web.json_response({'error': 'No file uploaded'}, status=400)

    # Parse the multipart form data
    reader = await request.multipart()
    field = await reader.next()  # Get the file field

    if field is None:
        return web.json_response({'error': 'No file field found'}, status=400)

    # Ensure the field is a file
    if field.name != 'file':
        return web.json_response({'error': 'Invalid field name'}, status=400)

    # Read the file data
    filename = field.filename
    file_path = os.path.join(UPLOAD_DIR, filename)

    # Save the file
    with open(file_path, 'wb') as f:
        while True:
            chunk = await field.read_chunk()  # Read the file in chunks
            if not chunk:
                break
            f.write(chunk)

    # Return a shareable link (in this case, just the filename)
    return web.json_response({'id': filename})

async def share_image(request):
    image_id = request.match_info.get('imageId')
    file_path = os.path.join(UPLOAD_DIR, image_id)

    if not os.path.isfile(file_path):
        return web.json_response({'error': 'Image not found'}, status=404)

    # Serve the image file
    return web.FileResponse(file_path)

app = web.Application()
app.router.add_post('/upload', upload_image)
app.router.add_get('/images/{imageId}', share_image)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)