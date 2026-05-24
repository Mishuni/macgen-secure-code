import os
import subprocess
from aiohttp import web
import json

# Define the storage directory for uploaded images
STORAGE_DIR = '/tmp/images/'

# Ensure the storage directory exists
os.makedirs(STORAGE_DIR, exist_ok=True)

async def create_gif(request):
    # Parse the multipart form data
    data = await request.post()
    
    # Validate and sanitize target size
    target_size = data.get('targetSize')
    if not target_size or 'x' not in target_size:
        return web.json_response({'error': 'Invalid target size format. Use width x height.'}, status=400)
    
    try:
        width, height = map(int, target_size.split('x'))
    except ValueError:
        return web.json_response({'error': 'Width and height must be integers.'}, status=400)

    # Validate delay
    delay = data.get('delay', 10)
    try:
        delay = int(delay)
    except ValueError:
        return web.json_response({'error': 'Delay must be an integer.'}, status=400)

    # Validate images
    images = data.getall('images')
    if not images:
        return web.json_response({'error': 'No images provided.'}, status=400)

    # Save images to the storage directory
    image_paths = []
    for i, image in enumerate(images):
        filename = os.path.join(STORAGE_DIR, f'image_{i}.png')
        with open(filename, 'wb') as f:
            f.write(image.file.read())
        image_paths.append(filename)

    # Create the GIF using ImageMagick
    gif_path = os.path.join(STORAGE_DIR, 'output.gif')
    append_reverted = data.get('appendReverted', 'false').lower() == 'true'
    
    if append_reverted:
        # Create a reversed version of the images
        image_paths_reversed = list(reversed(image_paths))
        image_paths.extend(image_paths_reversed)

    # Construct the ImageMagick command
    command = ['convert', '-delay', str(delay), '-resize', f'{width}x{height}'] + image_paths + [gif_path]
    
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        return web.json_response({'error': 'Failed to create GIF: ' + str(e)}, status=500)

    # Serve the created GIF
    with open(gif_path, 'rb') as f:
        gif_data = f.read()

    return web.Response(body=gif_data, content_type='image/gif')

app = web.Application()
app.router.add_post('/create-gif', create_gif)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)