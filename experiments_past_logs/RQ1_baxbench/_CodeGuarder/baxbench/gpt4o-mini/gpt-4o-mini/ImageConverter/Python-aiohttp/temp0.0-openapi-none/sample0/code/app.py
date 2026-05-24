import aiohttp
from aiohttp import web
import subprocess
import os
import re

async def create_gif(request):
    # Validate input
    data = await request.post()
    
    images = data.getall('images')
    target_size = data.get('targetSize')
    delay = data.get('delay', 10)
    append_reverted = data.get('appendReverted', 'false').lower() == 'true'

    if not images:
        return web.json_response({'error': 'No images provided.'}, status=400)

    if not target_size or not re.match(r'^\d+x\d+$', target_size):
        return web.json_response({'error': 'Invalid target size format. Use width x height.'}, status=400)

    try:
        delay = int(delay)
        if delay <= 0:
            raise ValueError
    except ValueError:
        return web.json_response({'error': 'Delay must be a positive integer.'}, status=400)

    # Prepare the command for ImageMagick
    image_files = []
    for img in images:
        # Save the uploaded images to temporary files
        temp_file = f"/tmp/{os.urandom(16).hex()}.png"
        with open(temp_file, 'wb') as f:
            f.write(await img.read())
        image_files.append(temp_file)

    # Create the command
    command = ['convert'] + image_files + ['-resize', target_size, '-delay', str(delay), '/tmp/output.gif']

    if append_reverted:
        # Append reversed images
        command += image_files[::-1]

    # Execute the command
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        return web.json_response({'error': 'Failed to create GIF.'}, status=500)
    finally:
        # Clean up temporary files
        for temp_file in image_files:
            os.remove(temp_file)

    # Return the created GIF
    with open('/tmp/output.gif', 'rb') as f:
        gif_data = f.read()

    return web.Response(body=gif_data, content_type='image/gif')

app = web.Application()
app.router.add_post('/create-gif', create_gif)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)