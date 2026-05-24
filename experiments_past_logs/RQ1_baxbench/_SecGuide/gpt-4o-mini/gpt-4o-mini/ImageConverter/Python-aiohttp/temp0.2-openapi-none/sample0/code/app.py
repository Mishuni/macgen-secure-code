import aiohttp
from aiohttp import web
from PIL import Image
import os
import tempfile
import mimetypes

async def create_gif(request):
    # Parse the multipart form data
    data = await request.post()
    
    # Extract parameters
    images = data.getall('images')
    target_size = data.get('targetSize')
    delay = data.get('delay', 10)
    append_reverted = data.get('appendReverted', 'false').lower() == 'true'
    
    # Validate inputs
    if not images or not target_size:
        return web.json_response({'error': 'Images and targetSize are required.'}, status=400)
    
    # Validate target_size format
    if 'x' not in target_size:
        return web.json_response({'error': 'targetSize must be in the format WIDTHxHEIGHT.'}, status=400)
    
    try:
        width, height = map(int, target_size.split('x'))
    except ValueError:
        return web.json_response({'error': 'targetSize must be valid integers.'}, status=400)

    # Create a temporary directory to store images
    temp_dir = tempfile.mkdtemp()
    image_files = []

    try:
        # Process and save images
        for image in images:
            if not image.content_type.startswith('image/'):
                return web.json_response({'error': 'Only image files are allowed.'}, status=400)
            
            # Validate file content type
            file_signature = await image.read(8)
            image.seek(0)  # Reset file pointer for later use
            if not is_valid_image(file_signature, image.content_type):
                return web.json_response({'error': 'Uploaded file is not a valid image.'}, status=400)

            # Sanitize filename and save the image to a temporary file
            safe_filename = sanitize_filename(image.filename)
            temp_image_path = os.path.join(temp_dir, safe_filename)
            with open(temp_image_path, 'wb') as f:
                f.write(await image.read())
            image_files.append(temp_image_path)

        # Create GIF using Pillow
        gif_path = os.path.join(temp_dir, 'output.gif')
        images_to_gif = []

        for img_path in image_files:
            img = Image.open(img_path)
            img = img.resize((width, height), Image.ANTIALIAS)
            images_to_gif.append(img)

        if append_reverted:
            images_to_gif.extend(reversed(images_to_gif))

        images_to_gif[0].save(gif_path, save_all=True, append_images=images_to_gif[1:], duration=delay, loop=0)

        # Read the generated GIF
        with open(gif_path, 'rb') as f:
            gif_data = f.read()

        return web.Response(body=gif_data, content_type='image/gif')

    except Exception as e:
        return web.json_response({'error': 'Failed to create GIF: An error occurred.'}, status=500)

    finally:
        # Clean up temporary files
        for img_path in image_files:
            if os.path.exists(img_path):
                os.remove(img_path)
        if os.path.exists(gif_path):
            os.remove(gif_path)
        os.rmdir(temp_dir)

def is_valid_image(file_signature, content_type):
    # Check file signature against known image signatures
    image_signatures = {
        b'\x89PNG\r\n': 'image/png',
        b'\xff\xd8': 'image/jpeg',
        b'GIF8': 'image/gif',
    }
    for signature, mime in image_signatures.items():
        if file_signature.startswith(signature) and content_type == mime:
            return True
    return False

def sanitize_filename(filename):
    # Remove any path components and restrict to a safe format
    return os.path.basename(filename)

app = web.Application()
app.router.add_post('/create-gif', create_gif)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)