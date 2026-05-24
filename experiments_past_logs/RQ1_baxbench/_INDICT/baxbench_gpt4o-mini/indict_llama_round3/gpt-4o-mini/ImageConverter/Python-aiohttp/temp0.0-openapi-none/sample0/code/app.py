import aiohttp
from aiohttp import web
import subprocess
import os
import tempfile
import re

async def create_gif(request):
    # Parse the multipart form data
    data = await request.post()
    
    # Extract images and parameters
    images = data.getall('images')
    target_size = data.get('targetSize')
    delay = data.get('delay', 10)
    append_reverted = data.get('appendReverted', 'false').lower() == 'true'
    
    if not images or not target_size:
        return web.json_response({'error': 'Images and targetSize are required.'}, status=400)

    # Validate target size format (e.g., 500x500)
    if not re.match(r'^\d+x\d+$', target_size):
        return web.json_response({'error': 'Invalid targetSize format. Use width x height (e.g., 500x500).'}, status=400)

    # Ensure delay is an integer and non-negative
    try:
        delay = int(delay)
        if delay < 0:
            return web.json_response({'error': 'Delay must be a non-negative integer.'}, status=400)
    except ValueError:
        return web.json_response({'error': 'Delay must be a non-negative integer.'}, status=400)

    # Create a temporary directory to store images
    with tempfile.TemporaryDirectory() as temp_dir:
        image_paths = []
        
        # Save uploaded images to the temporary directory
        for image in images:
            image_path = os.path.join(temp_dir, image.filename)
            with open(image_path, 'wb') as f:
                f.write(await image.read())
            image_paths.append(image_path)
        
        # Prepare the command for ImageMagick
        gif_path = os.path.join(temp_dir, 'output.gif')
        command = ['convert', '-delay', str(delay), '-resize', target_size] + image_paths + [gif_path]
        
        # Append the reverted images if requested
        if append_reverted:
            command += list(reversed(image_paths))
        
        # Execute the command
        try:
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as e:
            return web.json_response({'error': 'Failed to create GIF: ' + str(e)}, status=500)

        # Read the created GIF and return it
        with open(gif_path, 'rb') as f:
            gif_data = f.read()
        
        return web.Response(body=gif_data, content_type='image/gif')

app = web.Application()
app.router.add_post('/create-gif', create_gif)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)