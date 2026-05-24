import os
import aiohttp
from aiohttp import web
from werkzeug.utils import secure_filename
from PIL import Image
import io

# Directory to store uploaded images
UPLOAD_DIR = 'uploads'
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_image(file):
    try:
        img = Image.open(file)
        img.verify()  # Verify that it is an image
        return True
    except Exception:
        return False

async def upload_image(request):
    # Check if the request has the file
    reader = await request.multipart()
    field = await reader.next()
    
    if field is None or field.name != 'file':
        return web.json_response({'error': 'Invalid input'}, status=400)

    # Sanitize and validate the filename
    filename = secure_filename(field.filename)
    if not allowed_file(filename):
        return web.json_response({'error': 'Invalid file type'}, status=400)

    # Check file size before writing to disk
    size = 0
    file_bytes = io.BytesIO()
    while True:
        chunk = await field.read_chunk()  # 512 bytes by default
        if not chunk:
            break
        size += len(chunk)
        if size > MAX_FILE_SIZE:
            return web.json_response({'error': 'File too large'}, status=400)
        file_bytes.write(chunk)

    # Validate the image content
    file_bytes.seek(0)  # Reset the pointer to the beginning of the BytesIO object
    if not validate_image(file_bytes):
        return web.json_response({'error': 'Invalid image content'}, status=400)

    # Save the file to disk
    file_bytes.seek(0)  # Reset again before saving
    with open(os.path.join(UPLOAD_DIR, filename), 'wb') as f:
        f.write(file_bytes.read())

    # Return the shareable link (image ID is the filename)
    return web.json_response({'id': filename})

async def share_image(request):
    image_id = secure_filename(request.match_info['imageId'])
    file_path = os.path.join(UPLOAD_DIR, image_id)

    if not os.path.exists(file_path):
        return web.json_response({'error': 'Image not found'}, status=404)

    return web.FileResponse(file_path)

app = web.Application()
app.router.add_post('/upload', upload_image)
app.router.add_get('/images/{imageId}', share_image)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)