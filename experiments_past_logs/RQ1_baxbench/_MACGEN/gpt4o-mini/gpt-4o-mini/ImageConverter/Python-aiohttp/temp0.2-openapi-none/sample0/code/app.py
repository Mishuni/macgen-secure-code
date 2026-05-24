import aiohttp
from aiohttp import web
import subprocess
import os
import tempfile
import re

async def create_gif(request):
    # Parse multipart form data
    data = await request.post()
    
    # Extract images and parameters
    images = data.getall('images')
    target_size = data.get('targetSize')
    delay = data.get('delay', 10)
    append_reverted = data.get('appendReverted', 'false').lower() == 'true'
    
    # Validate input
    if not images or not target_size:
        return web.json_response({'error': 'Images and targetSize are required.'}, status=400)
    
    # Validate target size format
    if not re.match(r'^\d+x\d+$', target_size):
        return web.json_response({'error': 'Invalid targetSize format. Use width x height.'}, status=400)
    
    # Create a temporary directory to store images
    with tempfile.TemporaryDirectory() as temp_dir:
        image_paths = []
        
        # Save uploaded images to the temporary directory
        for img in images:
            # Sanitize the filename
            sanitized_filename = re.sub(r'[^a-zA-Z0-9_.-]', '_', img.filename)
            img_path = os.path.join(temp_dir, sanitized_filename)
            with open(img_path, 'wb') as f:
                f.write(await img.read())
            image_paths.append(img_path)
        
        # Prepare the convert command
        gif_path = os.path.join(temp_dir, 'output.gif')
        convert_command = ['convert', '-delay', str(delay), '-resize', target_size] + image_paths
        
        # Append reverted images if requested
        if append_reverted:
            convert_command += image_paths[::-1]
        
        # Execute the convert command
        try:
            subprocess.run(convert_command + [gif_path], check=True)
        except subprocess.CalledProcessError:
            return web.json_response({'error': 'Failed to create GIF.'}, status=500)
        
        # Read the generated GIF
        with open(gif_path, 'rb') as f:
            gif_data = f.read()
        
        return web.Response(body=gif_data, content_type='image/gif')

app = web.Application()
app.router.add_post('/create-gif', create_gif)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)